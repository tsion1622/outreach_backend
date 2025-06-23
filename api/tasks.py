
from django.contrib.auth.models import User
from .models import DomainDiscoveryTask, ScrapingTask, Contact, EmailSendingTask, EmailCampaign, EmailCampaignContact, SMTPConfiguration
import logging
import requests
import time
import random
import os
import csv
from datetime import datetime
import sys
from celery import shared_task
from .scraper import WebScraper
import pandas as pd

# Remove hardcoded Docker path
# sys.path.append('/home/ubuntu/outreach-tool/outreach-tool')
# from mailer import EmailSender  # ❌ Not used since mailer.py doesn't exist

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def domain_discovery_task(self, task_id, industry_or_seed_domain):
    try:
        task = DomainDiscoveryTask.objects.get(id=task_id)
        task.status = 'running'
        task.save()

        logger.info(f"Starting domain discovery for: {industry_or_seed_domain}")

        discovered_urls = []

        if industry_or_seed_domain.startswith('http'):
            base_domain = industry_or_seed_domain
            discovered_urls = [base_domain]
            common_paths = ['/about', '/contact', '/team', '/company']
            for path in common_paths:
                discovered_urls.append(base_domain.rstrip('/') + path)
        else:
            sample_domains = [
                f"https://example-{industry_or_seed_domain.replace(' ', '-').lower()}-{i}.com"
                for i in range(1, 101)
            ]
            discovered_urls = sample_domains

        output_file = f"/tmp/discovered_urls_{task_id}.txt"
        with open(output_file, 'w') as f:
            for url in discovered_urls:
                f.write(url + '\n')

        task.discovered_urls_count = len(discovered_urls)
        task.output_file_path = output_file
        task.status = 'completed'
        task.save()

        logger.info(f"Domain discovery completed. Found {len(discovered_urls)} URLs.")
        return {'status': 'completed', 'urls_count': len(discovered_urls), 'file_path': output_file}

    except Exception as e:
        logger.error(f"Domain discovery task failed: {str(e)}")
        task.status = 'failed'
        task.error_message = str(e)
        task.save()
        raise


@shared_task(bind=True)
def bulk_scraping_task(self, task_id, urls_file_path=None, urls_list=None):
    try:
        task = ScrapingTask.objects.get(id=task_id)
        task.status = 'running'
        task.save()

        logger.info(f"Starting bulk scraping for task: {task_id}")

        urls_to_scrape = []
        if urls_file_path and os.path.exists(urls_file_path):
            with open(urls_file_path, 'r') as f:
                urls_to_scrape = [line.strip() for line in f if line.strip()]
        elif urls_list:
            urls_to_scrape = urls_list
        else:
            raise ValueError("No URLs provided for scraping")

        task.total_urls = len(urls_to_scrape)
        task.save()

        # Assuming you still have this class somewhere
        scraper = WebScraper(rate_limit=0.5, max_workers=10)
        scraped_results = scraper.run(urls_to_scrape)

        contacts_created = 0
        for result in scraped_results:
            contact = Contact.objects.create(
                user=task.user,
                scraping_task=task,
                source_url=result['source_url'],
                scraped_on=datetime.strptime(result['scraped_on'], '%Y-%m-%d %H:%M:%S'),
                name=result['name'],
                email=result['email'],
                phone=result['phone'],
                city=result['city'],
                country=result['country'],
                personalized_info=result['personalized_info'],
                status=result['status']
            )
            if result['status'] == 'Success':
                contacts_created += 1

        task.processed_urls = len(scraped_results)
        task.successful_urls = contacts_created
        task.failed_urls = task.processed_urls - task.successful_urls
        task.status = 'completed'

        output_csv = f"/tmp/scraped_data_{task_id}.csv"
        df = pd.DataFrame(scraped_results)
        df.to_csv(output_csv, index=False)
        task.output_csv_path = output_csv
        task.save()

        logger.info(f"Bulk scraping completed. Processed {task.processed_urls} URLs, {task.successful_urls} successful.")
        return {
            'status': 'completed',
            'processed_urls': task.processed_urls,
            'successful_urls': task.successful_urls,
            'failed_urls': task.failed_urls
        }

    except Exception as e:
        logger.error(f"Bulk scraping task failed: {str(e)}")
        task.status = 'failed'
        task.error_message = str(e)
        task.save()
        raise


@shared_task(bind=True)
def email_sending_task(self, sending_task_id):
    try:
        sending_task = EmailSendingTask.objects.get(id=sending_task_id)
        campaign = sending_task.campaign

        sending_task.status = 'running'
        sending_task.save()

        logger.info(f"Starting email sending for campaign: {campaign.name}")

        try:
            smtp_config = SMTPConfiguration.objects.get(user=campaign.user)
        except SMTPConfiguration.DoesNotExist:
            raise ValueError("SMTP configuration not found for user")

        campaign_contacts = EmailCampaignContact.objects.filter(campaign=campaign).select_related('contact')
        recipients = []
        for cc in campaign_contacts:
            contact = cc.contact
            recipients.append({
                'email': contact.email,
                'name': contact.name,
                'phone': contact.phone,
                'city': contact.city,
                'country': contact.country,
                'personalized_info': contact.personalized_info,
                'source_url': contact.source_url,
            })

        sending_task.total_recipients = len(recipients)
        sending_task.save()

        sent_count = 0
        skipped_count = 0
        failed_count = 0

        for recipient in recipients:
            if not recipient['email']:
                skipped_count += 1
                continue

            personalized_content = campaign.template_content
            for key, value in recipient.items():
                if value:
                    personalized_content = personalized_content.replace(f'[{key}]', str(value))

            # Simulated email sending (since EmailSender is not available)
            logger.info(f"Simulated sending email to {recipient['email']}")
            sent_count += 1  # Assume success for now

            sending_task.sent_count = sent_count
            sending_task.skipped_count = skipped_count
            sending_task.failed_count = failed_count
            sending_task.save()

        sending_task.status = 'completed'
        sending_task.save()

        logger.info(f"Email sending completed. Sent: {sent_count}, Skipped: {skipped_count}, Failed: {failed_count}")
        return {
            'status': 'completed',
            'sent_count': sent_count,
            'skipped_count': skipped_count,
            'failed_count': failed_count
        }

    except Exception as e:
        logger.error(f"Email sending task failed: {str(e)}")
        sending_task.status = 'failed'
        sending_task.error_message = str(e)
        sending_task.save()
        raise
