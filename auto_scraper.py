#!/usr/bin/env python3
"""
NEET College Predictor - Automated Data Scraper
Automatically scrapes real NEET historical data from official websites
"""

import requests
import pandas as pd
import json
import time
import re
from bs4 import BeautifulSoup
from datetime import datetime
import os
from urllib.parse import urljoin, urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NEETDataScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.collected_data = []
        
    def scrape_mcc_website(self):
        """Scrape data from Medical Counselling Committee website"""
        logger.info("Scraping MCC website...")
        
        try:
            # MCC main website
            url = "https://mcc.nic.in/"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for counselling results and cutoffs
            links = soup.find_all('a', href=True)
            
            # Find links to counselling results
            result_links = []
            for link in links:
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                
                if any(keyword in href or keyword in text for keyword in [
                    'counselling', 'result', 'cutoff', 'allotment', 'seat', 'admission'
                ]):
                    result_links.append(urljoin(url, link['href']))
            
            logger.info(f"Found {len(result_links)} potential result links on MCC")
            
            # Scrape each result page
            for link in result_links[:5]:  # Limit to first 5 to avoid overwhelming
                try:
                    self.scrape_result_page(link, "MCC")
                    time.sleep(2)  # Be respectful
                except Exception as e:
                    logger.warning(f"Failed to scrape {link}: {e}")
                    
        except Exception as e:
            logger.error(f"Error scraping MCC website: {e}")
    
    def scrape_result_page(self, url, source):
        """Scrape individual result/cutoff pages"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for tables with admission data
            tables = soup.find_all('table')
            
            for table in tables:
                self.extract_data_from_table(table, source, url)
                
        except Exception as e:
            logger.warning(f"Error scraping result page {url}: {e}")
    
    def extract_data_from_table(self, table, source, url):
        """Extract admission data from HTML table"""
        try:
            rows = table.find_all('tr')
            if len(rows) < 2:  # Need at least header and one data row
                return
            
            # Try to identify if this table contains admission data
            header_row = rows[0]
            headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
            
            # Check if this looks like admission data
            admission_keywords = ['college', 'institute', 'rank', 'score', 'category', 'round', 'seat']
            if not any(keyword in ' '.join(headers) for keyword in admission_keywords):
                return
            
            logger.info(f"Found potential admission table with headers: {headers}")
            
            # Extract data rows
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) < 3:  # Need at least some data
                    continue
                
                row_data = [cell.get_text(strip=True) for cell in cells]
                
                # Try to parse the row data
                parsed_data = self.parse_admission_row(row_data, headers, source, url)
                if parsed_data:
                    self.collected_data.append(parsed_data)
                    
        except Exception as e:
            logger.warning(f"Error extracting data from table: {e}")
    
    def parse_admission_row(self, row_data, headers, source, url):
        """Parse a row of admission data"""
        try:
            # Initialize data structure
            data = {
                'source': source,
                'source_url': url,
                'scraped_date': datetime.now().isoformat()
            }
            
            # Map common header variations to our standard format
            header_mapping = {
                'college': ['college', 'institute', 'medical college', 'hospital'],
                'state': ['state', 'location', 'city'],
                'category': ['category', 'caste', 'quota', 'reservation'],
                'round': ['round', 'counselling round', 'phase'],
                'opening_rank': ['opening rank', 'start rank', 'min rank'],
                'closing_rank': ['closing rank', 'end rank', 'max rank'],
                'score': ['score', 'marks', 'neet score'],
                'seats': ['seats', 'total seats', 'available seats']
            }
            
            # Try to match headers and extract data
            for i, header in enumerate(headers):
                header_lower = header.lower()
                
                for field, keywords in header_mapping.items():
                    if any(keyword in header_lower for keyword in keywords):
                        if i < len(row_data):
                            data[field] = row_data[i]
                            break
            
            # Try to extract year from URL or data
            year_match = re.search(r'20\d{2}', url)
            if year_match:
                data['year'] = year_match.group()
            else:
                data['year'] = datetime.now().year
            
            # Validate that we have at least some meaningful data
            if len(data) > 4:  # At least source, url, date, and one data field
                return data
                
        except Exception as e:
            logger.warning(f"Error parsing row data: {e}")
        
        return None
    
    def scrape_state_websites(self):
        """Scrape data from state counselling websites"""
        state_websites = {
            'Maharashtra': 'https://mcc.nic.in/',
            'Karnataka': 'https://kea.kar.nic.in/',
            'Tamil Nadu': 'https://tnmedicalselection.net/',
            'Kerala': 'https://cee.kerala.gov.in/',
            'Delhi': 'https://dge.delhi.gov.in/',
            'Uttar Pradesh': 'https://upneet.gov.in/',
            'Bihar': 'https://bceceboard.bihar.gov.in/',
            'West Bengal': 'https://wbjeeb.nic.in/',
            'Gujarat': 'https://gujcet.gseb.org/',
            'Rajasthan': 'https://rajneet.nic.in/'
        }
        
        for state, url in state_websites.items():
            logger.info(f"Scraping {state} website: {url}")
            try:
                self.scrape_website(url, state)
                time.sleep(3)  # Be respectful to servers
            except Exception as e:
                logger.error(f"Error scraping {state} website: {e}")
    
    def scrape_website(self, url, source):
        """Generic website scraper"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for links to results/cutoffs
            links = soup.find_all('a', href=True)
            
            result_links = []
            for link in links:
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                
                if any(keyword in href or keyword in text for keyword in [
                    'result', 'cutoff', 'admission', 'counselling', 'allotment'
                ]):
                    full_url = urljoin(url, link['href'])
                    result_links.append(full_url)
            
            # Scrape result pages
            for link in result_links[:3]:  # Limit to avoid overwhelming
                try:
                    self.scrape_result_page(link, source)
                    time.sleep(2)
                except Exception as e:
                    logger.warning(f"Failed to scrape {link}: {e}")
                    
        except Exception as e:
            logger.error(f"Error scraping website {url}: {e}")
    
    def scrape_college_websites(self):
        """Scrape data from individual college websites"""
        college_websites = {
            'AIIMS Delhi': 'https://www.aiims.edu/',
            'JIPMER Puducherry': 'https://jipmer.edu.in/',
            'MAMC Delhi': 'https://www.mamc.ac.in/',
            'GMC Mumbai': 'https://www.gmc.edu.in/',
            'BHU Varanasi': 'https://www.bhu.ac.in/',
            'AMU Aligarh': 'https://www.amu.ac.in/',
            'KGMU Lucknow': 'https://kgmu.org/'
        }
        
        for college, url in college_websites.items():
            logger.info(f"Scraping {college} website: {url}")
            try:
                self.scrape_website(url, college)
                time.sleep(3)
            except Exception as e:
                logger.error(f"Error scraping {college} website: {e}")
    
    def clean_and_validate_data(self):
        """Clean and validate collected data"""
        logger.info("Cleaning and validating collected data...")
        
        cleaned_data = []
        
        for item in self.collected_data:
            try:
                # Clean college names
                if 'college' in item:
                    college = item['college']
                    # Standardize common college names
                    college_mappings = {
                        'aiims': 'AIIMS Delhi',
                        'jipmer': 'JIPMER Puducherry',
                        'mamc': 'MAMC Delhi',
                        'gmc': 'GMC Mumbai',
                        'bhu': 'BHU Varanasi',
                        'amu': 'AMU Aligarh',
                        'kgmu': 'KGMU Lucknow'
                    }
                    
                    for key, value in college_mappings.items():
                        if key in college.lower():
                            item['college'] = value
                            break
                
                # Clean categories
                if 'category' in item:
                    category = item['category'].lower()
                    if 'general' in category or 'ur' in category:
                        item['category'] = 'General'
                    elif 'obc' in category:
                        item['category'] = 'OBC'
                    elif 'sc' in category:
                        item['category'] = 'SC'
                    elif 'st' in category:
                        item['category'] = 'ST'
                    elif 'ews' in category:
                        item['category'] = 'EWS'
                
                # Clean rounds
                if 'round' in item:
                    round_text = item['round'].lower()
                    if 'round 1' in round_text or 'first' in round_text:
                        item['round'] = 'Round 1'
                    elif 'round 2' in round_text or 'second' in round_text:
                        item['round'] = 'Round 2'
                    elif 'mop' in round_text:
                        item['round'] = 'Mop Up'
                
                # Extract numeric values
                if 'opening_rank' in item:
                    rank_match = re.search(r'\d+', str(item['opening_rank']))
                    if rank_match:
                        item['opening_rank'] = int(rank_match.group())
                
                if 'closing_rank' in item:
                    rank_match = re.search(r'\d+', str(item['closing_rank']))
                    if rank_match:
                        item['closing_rank'] = int(rank_match.group())
                
                if 'score' in item:
                    score_match = re.search(r'\d+', str(item['score']))
                    if score_match:
                        item['score'] = int(score_match.group())
                
                # Validate required fields
                if 'college' in item and 'category' in item:
                    cleaned_data.append(item)
                    
            except Exception as e:
                logger.warning(f"Error cleaning data item: {e}")
        
        self.collected_data = cleaned_data
        logger.info(f"Cleaned data: {len(cleaned_data)} valid records")
    
    def generate_training_data(self):
        """Generate training data from scraped information"""
        logger.info("Generating training data...")
        
        training_records = []
        
        for item in self.collected_data:
            try:
                # Create training record
                record = {
                    'Year': item.get('year', 2023),
                    'College_Name': item.get('college', 'Unknown College'),
                    'State': item.get('state', 'Unknown State'),
                    'Category': item.get('category', 'General'),
                    'Counselling_Round': item.get('round', 'Round 1'),
                    'Opening_Rank': item.get('opening_rank', 0),
                    'Closing_Rank': item.get('closing_rank', 0),
                    'Total_Seats': item.get('seats', 0),
                    'Allotted_Seats': item.get('seats', 0),  # Assume all seats filled
                    'Score_Range': f"{item.get('score', 500)}-{item.get('score', 500)}",
                    'Source': item.get('source', 'Web Scraping'),
                    'Notes': f"Scraped from {item.get('source_url', 'Unknown URL')}"
                }
                
                training_records.append(record)
                
            except Exception as e:
                logger.warning(f"Error generating training record: {e}")
        
        return training_records
    
    def save_data(self, filename='scraped_neet_data.csv'):
        """Save scraped data to CSV"""
        logger.info(f"Saving scraped data to {filename}...")
        
        training_records = self.generate_training_data()
        
        if training_records:
            df = pd.DataFrame(training_records)
            df.to_csv(filename, index=False)
            logger.info(f"✅ Saved {len(training_records)} records to {filename}")
            return filename
        else:
            logger.warning("No valid data to save")
            return None
    
    def run_full_scraping(self):
        """Run complete scraping process"""
        logger.info("🚀 Starting automated NEET data scraping...")
        
        # Scrape all sources
        self.scrape_mcc_website()
        self.scrape_state_websites()
        self.scrape_college_websites()
        
        # Clean and validate data
        self.clean_and_validate_data()
        
        # Save data
        filename = self.save_data()
        
        logger.info("✅ Automated scraping completed!")
        return filename

def main():
    """Main function to run automated scraping"""
    print("🎓 NEET College Predictor - Automated Data Scraper")
    print("=" * 60)
    print("This will automatically scrape real NEET data from official websites")
    print("Please be patient as this may take several minutes...")
    print()
    
    scraper = NEETDataScraper()
    
    try:
        filename = scraper.run_full_scraping()
        
        if filename:
            print(f"\n✅ Scraping completed successfully!")
            print(f"📁 Data saved to: {filename}")
            print(f"📊 Total records collected: {len(scraper.collected_data)}")
            print("\n🚀 Next steps:")
            print("1. Review the scraped data in the CSV file")
            print("2. Run: python train_with_real_data.py")
            print("3. Test the website with real data")
        else:
            print("\n❌ No data was collected. This might be due to:")
            print("- Website structure changes")
            print("- Network connectivity issues")
            print("- Rate limiting by websites")
            print("\n💡 Try running the script again later")
            
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        print("💡 Check your internet connection and try again")

if __name__ == "__main__":
    main() 