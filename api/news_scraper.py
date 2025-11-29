"""
RapidVerify News Scraper & Verifier
Extracts news content from URLs and verifies against trusted sources
"""
import os
import re
import json
import requests
from datetime import datetime
from urllib.parse import urlparse, quote_plus
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash')
    else:
        gemini_model = None
except ImportError:
    genai = None
    gemini_model = None


class NewsScraper:
    """Scrapes news articles from URLs"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    
    def scrape_article(self, url: str) -> dict:
        """
        Scrape news article from URL
        Returns: {title, content, author, date, source, images, url}
        """
        result = {
            'url': url,
            'success': False,
            'title': '',
            'content': '',
            'summary': '',
            'author': '',
            'date': '',
            'source': '',
            'domain': '',
            'images': [],
            'error': None
        }
        
        try:
            # Parse domain
            parsed = urlparse(url)
            result['domain'] = parsed.netloc.replace('www.', '')
            result['source'] = self._get_source_name(result['domain'])
            
            # Fetch the page
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            result['title'] = self._extract_title(soup)
            
            # Extract content
            result['content'] = self._extract_content(soup)
            
            # Extract author
            result['author'] = self._extract_author(soup)
            
            # Extract date
            result['date'] = self._extract_date(soup)
            
            # Extract images
            result['images'] = self._extract_images(soup, url)
            
            # Generate summary
            if result['content']:
                result['summary'] = result['content'][:500] + '...' if len(result['content']) > 500 else result['content']
            
            result['success'] = True
            
        except requests.RequestException as e:
            result['error'] = f"Failed to fetch URL: {str(e)}"
        except ValueError as e:
            result['error'] = f"Invalid URL format: {str(e)}"
        except Exception as e:
            result['error'] = f"Error parsing article: {str(e)}"
            import traceback
            traceback.print_exc()
        
        return result
    
    def _get_source_name(self, domain: str) -> str:
        """Get human-readable source name from domain"""
        source_map = {
            'ndtv.com': 'NDTV',
            'timesofindia.indiatimes.com': 'Times of India',
            'hindustantimes.com': 'Hindustan Times',
            'thehindu.com': 'The Hindu',
            'indianexpress.com': 'Indian Express',
            'news18.com': 'News18',
            'indiatoday.in': 'India Today',
            'bbc.com': 'BBC News',
            'bbc.co.uk': 'BBC News',
            'reuters.com': 'Reuters',
            'apnews.com': 'Associated Press',
            'theguardian.com': 'The Guardian',
            'nytimes.com': 'New York Times',
            'washingtonpost.com': 'Washington Post',
            'cnn.com': 'CNN',
            'aljazeera.com': 'Al Jazeera',
            'pib.gov.in': 'Press Information Bureau (Government)',
            'who.int': 'World Health Organization',
        }
        return source_map.get(domain, domain.split('.')[0].title())
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        # Try common title selectors
        selectors = [
            'h1.article-title', 'h1.entry-title', 'h1.post-title',
            'h1[itemprop="headline"]', '.article-heading h1',
            'article h1', '.story-title', '.headline',
            'meta[property="og:title"]', 'meta[name="title"]',
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content', '').strip()
                return element.get_text().strip()
        
        # Fallback to title tag
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ''
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article body content"""
        # Remove unwanted elements
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 
                         'advertisement', '.ad', '.advertisement', '.social-share',
                         '.comments', '.related-articles']):
            tag.decompose()
        
        # Try common content selectors
        selectors = [
            'article .content', 'article .article-body', '.article-content',
            '.story-content', '.post-content', '.entry-content',
            '[itemprop="articleBody"]', '.article-text', '.story-body',
            'article p', '.news-content', '#article-body'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                content = ' '.join([el.get_text().strip() for el in elements])
                if len(content) > 100:  # Meaningful content
                    return self._clean_text(content)
        
        # Fallback: get all paragraphs from article or main
        article = soup.find('article') or soup.find('main') or soup.find('body')
        if article:
            paragraphs = article.find_all('p')
            content = ' '.join([p.get_text().strip() for p in paragraphs])
            return self._clean_text(content)
        
        return ''
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract article author"""
        selectors = [
            '[itemprop="author"]', '.author-name', '.byline',
            '.article-author', 'meta[name="author"]',
            '.writer', '[rel="author"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content', '').strip()
                return element.get_text().strip()
        
        return ''
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract publication date"""
        selectors = [
            'time[datetime]', '[itemprop="datePublished"]',
            '.article-date', '.publish-date', '.post-date',
            'meta[property="article:published_time"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content', '').strip()
                return element.get('datetime', '') or element.get_text().strip()
        
        return ''
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extract main images from article"""
        images = []
        
        # Try to find main article image
        selectors = [
            'article img', '.article-image img', '.featured-image img',
            '[itemprop="image"]', '.story-image img'
        ]
        
        for selector in selectors:
            for img in soup.select(selector)[:3]:  # Max 3 images
                src = img.get('src') or img.get('data-src')
                if src:
                    # Make absolute URL
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        parsed = urlparse(base_url)
                        src = f"{parsed.scheme}://{parsed.netloc}{src}"
                    
                    if src not in images:
                        images.append(src)
        
        return images
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common artifacts
        text = re.sub(r'(Share|Tweet|Email|Print|Comments?|Advertisement|Read more|Also read)[\s:]*', '', text, flags=re.IGNORECASE)
        return text.strip()


class NewsVerifier:
    """Verifies news against trusted sources"""
    
    def __init__(self):
        self.scraper = NewsScraper()
        
        # Fact-checking sources and their search URLs
        self.fact_check_sources = [
            {
                'name': 'Google Fact Check',
                'search_url': 'https://toolbox.google.com/factcheck/explorer/search/{query}',
                'api_url': 'https://factchecktools.googleapis.com/v1alpha1/claims:search',
                'type': 'api'
            },
            {
                'name': 'Snopes',
                'search_url': 'https://www.snopes.com/?s={query}',
                'type': 'search'
            },
            {
                'name': 'PolitiFact',
                'search_url': 'https://www.politifact.com/search/?q={query}',
                'type': 'search'
            },
            {
                'name': 'FactCheck.org',
                'search_url': 'https://www.factcheck.org/?s={query}',
                'type': 'search'
            },
            {
                'name': 'Alt News (India)',
                'search_url': 'https://www.altnews.in/?s={query}',
                'type': 'search'
            },
            {
                'name': 'BOOM FactCheck (India)',
                'search_url': 'https://www.boomlive.in/search?query={query}',
                'type': 'search'
            },
            {
                'name': 'PIB Fact Check',
                'search_url': 'https://pib.gov.in/factcheck.aspx',
                'type': 'search'
            }
        ]
        
        # Trusted news sources by credibility tier
        self.trusted_sources = {
            'tier1': [  # Highly credible - official/wire services
                'pib.gov.in', 'who.int', 'cdc.gov', 'reuters.com', 
                'apnews.com', 'afp.com', 'pti.in'
            ],
            'tier2': [  # Major credible news organizations
                'bbc.com', 'bbc.co.uk', 'nytimes.com', 'washingtonpost.com',
                'theguardian.com', 'economist.com', 'thehindu.com',
                'indianexpress.com', 'ndtv.com', 'livemint.com'
            ],
            'tier3': [  # Generally reliable
                'hindustantimes.com', 'timesofindia.indiatimes.com',
                'news18.com', 'indiatoday.in', 'cnn.com', 'aljazeera.com',
                'firstpost.com', 'moneycontrol.com', 'businesstoday.in',
                'deccanherald.com', 'scroll.in', 'thewire.in', 'theprint.in'
            ]
        }
    
    def verify_url(self, url: str) -> dict:
        """
        Verify a news article by its URL
        1. Scrape the article
        2. Extract key claims
        3. Search fact-check sources
        4. Cross-reference with trusted sources
        5. Return verification with citations
        """
        result = {
            'success': False,
            'url': url,
            'article': None,
            'verification': {
                'score': 0.5,
                'status': 'investigating',
                'verdict': '',
                'confidence': 'medium'
            },
            'source_credibility': {
                'tier': None,
                'score': 0.5,
                'is_known_source': False
            },
            'fact_checks': [],
            'cross_references': [],
            'key_claims': [],
            'warnings': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 1: Scrape the article
        article = self.scraper.scrape_article(url)
        result['article'] = article
        
        if not article['success']:
            result['warnings'].append(f"Could not scrape article: {article.get('error', 'Unknown error')}")
            return result
        
        # Step 2: Check source credibility
        source_cred = self._check_source_credibility(article['domain'])
        result['source_credibility'] = source_cred
        
        # Step 3: Extract key claims using AI (if available) or keywords
        key_claims = self._extract_key_claims(article['title'], article['content'])
        result['key_claims'] = key_claims
        
        # Step 4: Search fact-check sources
        fact_checks = self._search_fact_checks(article['title'], key_claims)
        result['fact_checks'] = fact_checks
        
        # Step 5: Search for cross-references in trusted sources
        cross_refs = self._search_cross_references(article['title'], key_claims)
        result['cross_references'] = cross_refs
        
        # Step 6: Calculate final verification score
        verification = self._calculate_verification(source_cred, fact_checks, cross_refs, article)
        result['verification'] = verification
        
        result['success'] = True
        return result
    
    def verify_text(self, text: str) -> dict:
        """Verify a text claim (WhatsApp message, etc.) - PRODUCTION VERSION"""
        result = {
            'success': True,
            'text': text,
            'verification': {
                'score': 0.3,  # Start suspicious (unknown source)
                'status': 'investigating',
                'verdict': '',
                'confidence': 'medium'
            },
            'fact_checks': [],
            'cross_references': [],
            'key_claims': [],
            'warnings': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 1: Check for fake news patterns FIRST (heavily weighted)
        fake_score, warnings = self._check_fake_patterns(text)
        result['warnings'] = warnings
        
        # DEBUG: Check if this is a simple factual statement
        is_simple_factual = self._is_simple_factual_statement(text)
        if is_simple_factual:
            print(f"✅ Detected simple factual statement: '{text[:50]}...'")
        
        # Step 2: Extract claims using AI
        key_claims = self._extract_key_claims(text, text)
        result['key_claims'] = key_claims
        
        # Step 3: Search fact-checks
        fact_checks = self._search_fact_checks(text, key_claims)
        result['fact_checks'] = fact_checks
        
        # Step 4: Search cross-references (includes Google Search scraping)
        cross_refs = self._search_cross_references(text, key_claims)
        result['cross_references'] = cross_refs
        
        # Step 5: Use Gemini AI for proper fact-checking analysis (with Google search results)
        ai_score = None
        ai_verdict = None
        if gemini_model:
            try:
                # Pass Google search results to AI for better context
                ai_analysis = self._ai_verify_claim(text, fact_checks, key_claims, cross_refs)
                ai_score = ai_analysis.get('score')
                ai_verdict = ai_analysis.get('verdict')
                if ai_analysis.get('warnings'):
                    result['warnings'].extend(ai_analysis['warnings'])
            except Exception as e:
                print(f"⚠️ AI verification failed: {e}")
        
        # Step 6: Calculate final score (PRODUCTION - ULTRA STRICT)
        # CRITICAL RULE: Fake patterns and fact-check debunks have ABSOLUTE PRIORITY
        
        # CRITICAL FIX: Check for simple factual statements FIRST (before defaulting to suspicious)
        is_simple_factual = self._is_simple_factual_statement(text)
        
        # Start with LOW score for unknown source (default suspicious)
        # But check if content seems legitimate first
        text_lower = text.lower()
        has_credible_indicators = any(phrase in text_lower for phrase in [
            'according to', 'official statement', 'press release', 'government announced',
            'ministry said', 'confirmed by', 'study shows', 'research indicates', 'experts say',
            'reuters', 'ap news', 'associated press', 'bbc', 'reported by'
        ])
        
        # STEP 1: HEAVILY penalize fake patterns FIRST (ABSOLUTE PRIORITY)
        # BUT: Simple factual statements are EXEMPT from fake pattern penalties (unless severe)
        has_severe_fake_patterns = False
        
        # CRITICAL FIX: For simple factual statements, only apply penalties for SEVERE patterns
        if is_simple_factual:
            print(f"✅ Simple factual statement detected: '{text[:50]}...'")
            # Only penalize if there are SEVERE fake patterns (scams, urgency manipulation)
            if fake_score > 0.7:
                base_score = 0.15  # Even factual statements with severe scams are suspicious
                has_severe_fake_patterns = True
            elif fake_score > 0.5:
                base_score = 0.3  # Moderate penalty for factual statements with manipulation
                has_severe_fake_patterns = True
            else:
                # Simple factual statements with no severe patterns = HIGH SCORE
                base_score = 0.75  # Simple factual statements are likely true (e.g., "X is PM of Y")
                print(f"✅ No severe fake patterns - treating as credible factual statement")
        else:
            # For non-factual statements, apply full fake pattern penalties
            if fake_score > 0.7:
                base_score = 0.05  # SCAM - Extremely suspicious (multiple severe patterns)
                has_severe_fake_patterns = True
            elif fake_score > 0.5:
                base_score = 0.08  # Very suspicious - likely fake/scam
                has_severe_fake_patterns = True
            elif fake_score > 0.3:
                base_score = 0.12  # Suspicious - multiple red flags
                has_severe_fake_patterns = True
            elif fake_score > 0.1:
                base_score = 0.18  # Somewhat suspicious
            elif has_credible_indicators:
                base_score = 0.5  # Has credible language and no fake patterns
            else:
                base_score = 0.25  # Still cautious (unknown source)
        
        # STEP 2: Check fact-check results (ABSOLUTE PRIORITY - overrides everything)
        debunked_count = 0
        verified_count = 0
        for fc in fact_checks:
            if fc.get('type') not in ['manual_search', 'manual']:
                rating = fc.get('rating', '').lower()
                if rating in ['false', 'fake', 'pants on fire', 'mostly false', 'debunked', 'hoax', 'misleading', 'incorrect']:
                    debunked_count += 1
                elif rating in ['true', 'mostly true', 'correct', 'verified']:
                    verified_count += 1
        
        # CRITICAL: If ANY fact-check debunks it, score MUST be very low (ABSOLUTE)
        if debunked_count >= 2:
            base_score = 0.05  # Multiple debunks = definitely fake (ABSOLUTE)
        elif debunked_count >= 1:
            base_score = min(base_score, 0.15)  # Single debunk = very suspicious (ABSOLUTE)
        
        # STEP 3: Verifications ONLY help if NO fake patterns and NO debunks
        # If fake patterns exist, verifications are IGNORED (likely manipulation)
        # FIX: Simple factual statements don't need verifications to be credible
        if not has_severe_fake_patterns and debunked_count == 0:
            if verified_count >= 3:
                base_score = min(base_score + 0.25, 0.8)  # Multiple verifications
            elif verified_count >= 2:
                base_score = min(base_score + 0.15, 0.75)  # Two verifications
            elif verified_count >= 1:
                base_score = min(base_score + 0.08, 0.65)  # Single verification (small boost)
            # FIX: Simple factual statements are credible even without verifications
            elif is_simple_factual and verified_count == 0:
                # Don't penalize - factual statements are self-evident
                pass
        # If fake patterns exist, verifications are SUSPICIOUS (likely fake verification)
        elif has_severe_fake_patterns and verified_count > 0:
            base_score = max(0.05, base_score - 0.05)  # Penalize - likely fake verification
        
        # STEP 4: Use AI score (but simple factual statements have priority)
        if ai_score is not None:
            # CRITICAL FIX: For simple factual statements, prioritize base_score (which is already high)
            if is_simple_factual and not has_severe_fake_patterns and debunked_count == 0:
                # Only trust AI if it STRONGLY debunks (very low score) - otherwise trust the factual statement
                if ai_score < 0.15:
                     base_score = ai_score
                     print(f"⚠️ AI strongly debunked factual statement ({ai_score}) - trusting AI")
                # If AI agrees it's true or is uncertain, prioritize base_score (factual statements are self-evident)
                elif ai_score >= 0.5:
                    base_score = max(base_score, ai_score)  # Use higher of the two
                else:
                    # AI is uncertain (0.15-0.5), but factual statements are likely true - trust base_score more
                    base_score = (base_score * 0.8) + (ai_score * 0.2)  # Heavily weight base_score
                    print(f"✅ AI uncertain ({ai_score}) but factual statement detected - trusting base_score ({base_score})")
            # If AI says fake, trust it ABSOLUTELY (unless it's a simple factual statement)
            elif ai_score < 0.25 and not is_simple_factual:
                base_score = min(base_score, ai_score)  # AI says fake = use lower score
            # If fake patterns detected, AI score cannot save it
            elif has_severe_fake_patterns:
                base_score = min(base_score, 0.25)  # Cap at suspicious
            # If debunked, AI cannot override
            elif debunked_count > 0:
                base_score = min(base_score, 0.2)  # Cap at very suspicious
            # Otherwise, blend AI with base (but AI has more weight if it's lower)
            else:
                if ai_score < base_score:
                    base_score = (ai_score * 0.7) + (base_score * 0.3)  # Trust AI if it's more strict
                else:
                    base_score = (ai_score * 0.4) + (base_score * 0.6)  # Be cautious if AI is lenient
        else:
            # No AI = be MORE cautious, reduce score
            # BUT: For simple factual statements, don't reduce as much
            if is_simple_factual and not has_severe_fake_patterns:
                base_score = base_score * 0.95  # Only slight reduction for factual statements
            else:
                base_score = base_score * 0.9
        
        # STEP 5: Cross-references ONLY help if NO fake patterns and score already decent
        # Cross-refs are weak evidence - cannot override red flags
        if not has_severe_fake_patterns and debunked_count == 0 and base_score > 0.5:
            if cross_refs and len(cross_refs) >= 3:
                base_score = min(base_score + 0.05, 0.75)  # Small boost only
            elif cross_refs and len(cross_refs) >= 2:
                base_score = min(base_score + 0.03, 0.7)
        
        # STEP 6: ABSOLUTE CAPS - fake patterns CANNOT be overcome
        # BUT: Simple factual statements can overcome minor fake patterns
        if has_severe_fake_patterns:
            # FIX: Don't cap simple factual statements if they have no fake patterns
            if not is_simple_factual or fake_score > 0.3:
                base_score = min(base_score, 0.25)  # MAX 0.25 if fake patterns detected
        if debunked_count > 0:
            # FIX: Don't cap simple factual statements unless actually debunked by fact-checks
            if not is_simple_factual or debunked_count >= 2:
                base_score = min(base_score, 0.2)  # MAX 0.2 if debunked
        if fake_score > 0.1 and debunked_count == 0:
            # FIX: Simple factual statements should not be capped if no severe patterns
            if is_simple_factual and fake_score < 0.3:
                pass  # Don't cap - allow factual statements through
            else:
                base_score = min(base_score, 0.35)  # MAX 0.35 if any fake patterns (no debunk)
        
        # Final clamp - ensure reasonable bounds
        score = max(0.05, min(0.95, round(base_score, 2)))
        
        # Generate verdict
        if ai_verdict:
            verdict = ai_verdict
        else:
            verdict = self._generate_verdict(score, fact_checks, cross_refs)
        
        result['verification'] = {
            'score': score,
            'status': 'debunked' if score < 0.4 else 'verified' if score > 0.7 else 'investigating',
            'verdict': verdict,
            'confidence': 'high' if (fact_checks and ai_score is not None) else 'medium' if fact_checks else 'low'
        }
        
        return result
    
    def _check_source_credibility(self, domain: str) -> dict:
        """Check if source domain is credible"""
        domain = domain.lower().replace('www.', '')
        
        for tier, sources in self.trusted_sources.items():
            if any(s in domain for s in sources):
                tier_scores = {'tier1': 0.95, 'tier2': 0.85, 'tier3': 0.75}
                return {
                    'tier': tier,
                    'score': tier_scores[tier],
                    'is_known_source': True,
                    'source_name': self.scraper._get_source_name(domain)
                }
        
        # Check for suspicious patterns
        suspicious = ['blogspot', 'wordpress.com', 'medium.com', 'substack']
        if any(s in domain for s in suspicious):
            return {
                'tier': 'unverified',
                'score': 0.4,
                'is_known_source': False,
                'warning': 'User-generated content platform'
            }
        
        # Unknown sources are SUSPICIOUS, not neutral
        return {
            'tier': 'unknown',
            'score': 0.3,  # Suspicious, not neutral
            'is_known_source': False,
            'warning': 'Unknown source - verify carefully'
        }
    
    def _extract_key_claims(self, title: str, content: str) -> list:
        """Extract key factual claims from article"""
        claims = []
        
        # Use Gemini if available
        if gemini_model:
            try:
                prompt = f"""Extract the main factual claims from this news article that can be fact-checked.
                
Title: {title}
Content: {content[:2000]}

Return as JSON array of strings, max 5 claims. Focus on:
- Specific events, dates, numbers
- Quotes attributed to people
- Statistical claims
- Policy announcements

Return ONLY the JSON array, no other text."""

                response = gemini_model.generate_content(prompt)
                json_match = re.search(r'\[[\s\S]*\]', response.text)
                if json_match:
                    claims = json.loads(json_match.group())[:5]
            except ValueError as e:
                print(f"AI claim extraction failed (invalid response): {e}")
            except Exception as e:
                print(f"AI claim extraction failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback: Use title and first sentences
        if not claims:
            claims = [title] if title else []
            sentences = re.split(r'[.!?]', content[:500])
            for sent in sentences[:3]:
                sent = sent.strip()
                if len(sent) > 30 and sent not in claims:
                    claims.append(sent)
        
        return claims[:5]
    
    def _search_fact_checks(self, query: str, claims: list) -> list:
        """Search fact-checking websites for related checks - PRODUCTION VERSION"""
        fact_checks = []
        
        # CRITICAL: Try Google Fact Check API first (most reliable)
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if google_api_key:
            try:
                api_url = 'https://factchecktools.googleapis.com/v1alpha1/claims:search'
                
                # Search main query
                params = {
                    'key': google_api_key,
                    'query': query[:200],
                    'languageCode': 'en',
                    'maxAgeDays': 365  # Check last year
                }
                response = requests.get(api_url, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    for claim in data.get('claims', [])[:10]:  # Get more results
                        reviews = claim.get('claimReview', [])
                        if reviews:
                            for review in reviews[:2]:  # Get up to 2 reviews per claim
                                rating = review.get('textualRating', '').lower()
                                publisher = review.get('publisher', {})
                                
                                fact_checks.append({
                                    'claim': claim.get('text', ''),
                                    'claimant': claim.get('claimant', 'Unknown'),
                                    'rating': review.get('textualRating', 'Unknown'),
                                    'source': publisher.get('name', 'Unknown'),
                                    'url': review.get('url', ''),
                                    'date': review.get('reviewDate', ''),
                                    'type': 'api_verified',
                                    'relevance': 'high'
                                })
                
                # Also search individual claims if available
                if claims:
                    for claim_text in claims[:3]:  # Check top 3 claims
                        params['query'] = claim_text[:200]
                        try:
                            response = requests.get(api_url, params=params, timeout=10)
                            if response.status_code == 200:
                                data = response.json()
                                for claim in data.get('claims', [])[:3]:
                                    reviews = claim.get('claimReview', [])
                                    if reviews:
                                        review = reviews[0]
                                        rating = review.get('textualRating', '').lower()
                                        if rating in ['false', 'fake', 'debunked', 'hoax', 'pants on fire']:
                                            fact_checks.append({
                                                'claim': claim.get('text', ''),
                                                'rating': review.get('textualRating', 'Unknown'),
                                                'source': review.get('publisher', {}).get('name', 'Unknown'),
                                                'url': review.get('url', ''),
                                                'type': 'api_verified',
                                                'relevance': 'very_high'
                                            })
                        except:
                            pass  # Continue if one claim search fails
                            
            except Exception as e:
                print(f"⚠️ Google Fact Check API error: {e}")
        
        # Add manual search links (for user verification)
        search_query = quote_plus(query[:100])
        for source in self.fact_check_sources[:6]:  # Include all major sources
            fact_checks.append({
                'source': source['name'],
                'search_url': source['search_url'].format(query=search_query),
                'type': 'manual_search',
                'note': f"Search {source['name']} for related fact-checks"
            })
        
        return fact_checks
    
    def _google_search(self, query: str, num_results: int = 10) -> list:
        """Search Google and scrape results"""
        search_results = []
        
        try:
            # Build Google search URL
            search_query = quote_plus(query[:200])
            search_url = f'https://www.google.com/search?q={search_query}&num={num_results}'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results (Google's structure)
            # Try multiple selectors for different Google layouts
            result_divs = soup.find_all('div', class_='g') or soup.find_all('div', {'data-ved': True})
            
            for idx, div in enumerate(result_divs[:num_results]):
                try:
                    # Extract title
                    title_elem = div.find('h3') or div.find('a', {'data-ved': True})
                    title = title_elem.get_text(strip=True) if title_elem else ''
                    
                    # Extract URL
                    link_elem = div.find('a', href=True)
                    url = ''
                    if link_elem:
                        url = link_elem.get('href', '')
                        # Clean Google redirect URLs
                        if url.startswith('/url?q='):
                            url = url.split('/url?q=')[1].split('&')[0]
                        elif url.startswith('/url?'):
                            import urllib.parse
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                            url = parsed.get('q', [''])[0]
                    
                    # Extract snippet
                    snippet_elem = div.find('span', class_='aCOpRe') or div.find('div', class_='VwiC3b') or div.find('span', class_='st')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    if title and url:
                        search_results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'rank': idx + 1
                        })
                except Exception as e:
                    continue
            
            # If no results found with standard selectors, try alternative method
            if not search_results:
                # Try scraping from search result links
                links = soup.find_all('a', href=True)
                for link in links[:num_results]:
                    href = link.get('href', '')
                    if href.startswith('/url?q=') or href.startswith('http'):
                        title = link.get_text(strip=True)
                        if title and len(title) > 10:  # Valid title
                            if href.startswith('/url?q='):
                                url = href.split('/url?q=')[1].split('&')[0]
                            else:
                                url = href
                            
                            if url and url.startswith('http'):
                                search_results.append({
                                    'title': title,
                                    'url': url,
                                    'snippet': '',
                                    'rank': len(search_results) + 1
                                })
                                if len(search_results) >= num_results:
                                    break
            
        except requests.RequestException as e:
            print(f"⚠️ Google Search request error: {e}")
        except Exception as e:
            print(f"⚠️ Google Search parsing error: {e}")
        
        return search_results
    
    def _google_search(self, query: str, num_results: int = 10) -> list:
        """
        Perform a Google search and scrape results
        Note: This is a basic scraper. For production, use Custom Search JSON API.
        """
        results = []
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
            
            # Search URL
            url = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}"
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ Google Search failed: {response.status_code}")
                return results
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse search results (div.g)
            for g in soup.select('div.g'):
                # Extract link
                link = g.select_one('a')
                if not link:
                    continue
                    
                href = link.get('href')
                if not href or not href.startswith('http'):
                    continue
                    
                # Extract title
                title_el = g.select_one('h3')
                title = title_el.get_text() if title_el else href
                
                # Extract snippet
                snippet_el = g.select_one('div.VwiC3b') or g.select_one('div.IsZvec') or g.select_one('div.s')
                snippet = snippet_el.get_text() if snippet_el else ''
                
                results.append({
                    'title': title,
                    'url': href,
                    'snippet': snippet,
                    'rank': len(results) + 1
                })
                
                if len(results) >= num_results:
                    break
                    
        except Exception as e:
            print(f"⚠️ Google Search error: {e}")
            
        return results

    def _search_cross_references(self, query: str, claims: list) -> list:
        """Search trusted news sources for corroborating reports - ENHANCED WITH GOOGLE SEARCH"""
        cross_refs = []
        
        # NEW: Perform actual Google Search and scrape results
        print(f"🔍 Performing Google Search for: {query[:50]}...")
        google_results = self._google_search(query, num_results=10)
        
        # Add scraped Google search results
        for result in google_results[:5]:  # Top 5 results
            # Check if it's from a trusted source
            domain = urlparse(result['url']).netloc.replace('www.', '')
            is_trusted = any(trusted in domain.lower() for trusted in [
                'reuters', 'bbc', 'ap.org', 'pib.gov', 'who.int', 'cdc.gov',
                'thehindu', 'indianexpress', 'timesofindia', 'hindustantimes'
            ])
            
            cross_refs.append({
                'source': result['title'],
                'url': result['url'],
                'snippet': result['snippet'],
                'type': 'google_search',
                'relevance': 'high' if is_trusted else 'medium',
                'rank': result['rank']
            })
        
        # Add Google News search link
        search_query = quote_plus(query[:100])
        cross_refs.append({
            'source': 'Google News',
            'search_url': f'https://news.google.com/search?q={search_query}',
            'type': 'search',
            'note': 'Search Google News for related coverage'
        })
        
        # Add trusted source search links
        cross_refs.append({
            'source': 'Reuters',
            'search_url': f'https://www.reuters.com/search/news?query={search_query}',
            'type': 'search'
        })
        
        cross_refs.append({
            'source': 'PIB India',
            'search_url': f'https://pib.gov.in/allRel.aspx',
            'type': 'search',
            'note': 'Check official government press releases'
        })
        
        return cross_refs
    
    def _ai_verify_claim(self, text: str, fact_checks: list, key_claims: list, cross_refs: list = None) -> dict:
        """Use Gemini AI to verify claim against fact-checks, Google search results, and patterns - PRODUCTION STRICT VERSION"""
        if not gemini_model:
            print("⚠️ Gemini model not available - skipping AI verification")
            return {'score': None, 'verdict': None, 'warnings': []}
        
        try:
            # Build fact-check summary
            fact_check_summary = []
            debunked_found = False
            verified_found = False
            
            for fc in fact_checks[:10]:  # Check more fact-checks
                if fc.get('type') != 'manual_search':
                    rating = fc.get('rating', '').lower()
                    source = fc.get('source', 'Unknown')
                    fact_check_summary.append(f"- {source}: {rating}")
                    
                    if rating in ['false', 'fake', 'debunked', 'hoax', 'pants on fire', 'mostly false']:
                        debunked_found = True
                    elif rating in ['true', 'verified', 'correct', 'mostly true']:
                        verified_found = True
            
            fact_check_text = '\n'.join(fact_check_summary) if fact_check_summary else "No fact-check results found"
            
            # Build Google Search results summary
            google_search_summary = []
            if cross_refs:
                for ref in cross_refs:
                    if ref.get('type') == 'google_search' and ref.get('url'):
                        title = ref.get('source', 'Unknown')
                        url = ref.get('url', '')
                        snippet = ref.get('snippet', '')
                        google_search_summary.append(f"- {title}\n  URL: {url}\n  Snippet: {snippet[:200]}")
            
            google_search_text = '\n'.join(google_search_summary[:5]) if google_search_summary else "No Google search results found"
            
            # BALANCED prompt - strict for scams, fair for legitimate claims
            # Check if this is a simple factual statement
            is_factual = self._is_simple_factual_statement(text)
            
            prompt = f"""You are a professional fact-checker AI. Your job is to accurately verify claims. Be STRICT for scams and manipulation, but FAIR for legitimate factual statements.

CLAIM TO VERIFY:
"{text[:1000]}"

KEY CLAIMS:
{chr(10).join(f'- {c[:200]}' for c in key_claims[:3])}

FACT-CHECK RESULTS:
{fact_check_text}

GOOGLE SEARCH RESULTS (scraped from web):
{google_search_text}

IS THIS A SIMPLE FACTUAL STATEMENT? {is_factual}
Examples: "narendramodi is the pm of india", "X is the PM of Y", "X is Y", "X happened on Y date"

**IMPORTANT**: Use the Google Search results above to verify the claim. If multiple trusted sources (Reuters, BBC, official government sites) confirm the claim, score it higher. If they contradict it, score it lower.

**CRITICAL RULE FOR SIMPLE FACTUAL STATEMENTS:**
If the claim is a simple factual statement (like "X is the PM of Y" or "X is Y"), you MUST:
1. Check if the fact is CORRECT based on your knowledge
2. If CORRECT → Score 0.75-0.9 (HIGH - these are verifiable facts, don't penalize for lack of fact-checks)
3. If INCORRECT → Score 0.1-0.2 (LOW - but only if you're CERTAIN it's wrong)
4. If UNCERTAIN → Score 0.6-0.7 (MEDIUM-HIGH - give benefit of doubt to factual statements)
5. DO NOT penalize simple factual statements just because they lack fact-checks - these are self-evident facts

ABSOLUTE RULES (MUST FOLLOW):
1. If ANY fact-check says FALSE/FAKE/DEBUNKED/HOAX → Score MUST be 0.15 or below
2. If claim contains "free money", "lottery", "claim prize", "forward to claim" → Score MUST be 0.1 or below (SCAM)
3. If claim has "share before deleted", "forward immediately", "urgent share" → Score MUST be 0.2 or below (MANIPULATION)
4. If claim has urgency/manipulation tactics → Score MUST be below 0.3
5. **CRITICAL: SIMPLE FACTUAL STATEMENTS** (e.g., "narendramodi is the pm of india", "X is the PM of Y", "X happened on Y date") → 
   - If factually CORRECT → Score 0.75-0.9 (HIGH - these are verifiable facts)
   - If factually INCORRECT → Score 0.1-0.2 (LOW - but only if you know it's wrong)
   - If UNCERTAIN → Score 0.6-0.7 (MEDIUM-HIGH - give benefit of doubt)
   - DO NOT penalize simple factual statements just because they lack fact-checks
6. **LEGITIMATE NEWS** without red flags → Score 0.6-0.8 (don't penalize for lack of fact-checks if no suspicious patterns)
7. Only score above 0.7 if MULTIPLE (3+) trusted sources verify it AND no red flags, OR if it's a simple factual statement
8. If claim asks to forward/share → Score MUST be below 0.25 (VIRAL MANIPULATION)

RED FLAGS (AUTOMATIC LOW SCORE):
- Scam indicators: free money, lottery, claim prize, forward to get, share to claim, government giving money
- Urgency tactics: share before deleted, forward immediately, act now, limited time, urgent
- Sensationalist: shocking, breaking, unbelievable, secret, exposed, hidden truth
- Health misinformation: miracle cure, doctors shocked, big pharma hiding, instant cure
- Government schemes: free scheme, pm giving, official announcement (without source)
- Forward manipulation: forward this, share this, send to 10 people, tell everyone
- Numbers with money: large amounts (10000, 50000) + free/claim/money = SCAM

LEGITIMATE PATTERNS (HIGHER SCORE):
- Simple factual statements: "X is Y", "X happened", "X said Y"
- Political facts: "X is the PM/President/Minister of Y"
- Historical facts: "X happened on Y date"
- Official positions: "X holds position Y"
- News reports without manipulation tactics

SCORING GUIDELINES:
- Score 0.05-0.15: Clear scam or debunked misinformation
- Score 0.15-0.25: High suspicion, likely fake
- Score 0.25-0.4: Suspicious, needs verification
- Score 0.4-0.6: Uncertain, verify with sources
- Score 0.6-0.75: Likely credible (simple facts, legitimate news)
- Score 0.75-0.9: Credible, verified by multiple sources OR simple factual statements
- Score 0.9+: Highly credible, official sources

Respond ONLY in valid JSON (no markdown, no code blocks):
{{
    "score": 0.0-1.0,
    "verdict": "clear verdict explaining why (be specific about red flags or why it's credible)",
    "is_fake": true/false,
    "red_flags": ["specific red flags found"] or [],
    "confidence": "high/medium/low"
}}

CRITICAL: 
- For SCAMS/MANIPULATION → Score LOW (0.1-0.3)
- For SIMPLE FACTUAL STATEMENTS → Score HIGH (0.7-0.9) if factually correct
- For LEGITIMATE NEWS without red flags → Score MEDIUM-HIGH (0.6-0.8)
- Only default to suspicious (0.3) if there are actual red flags or manipulation tactics"""

            response = gemini_model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,  # Low temperature for consistent, strict results
                    "top_p": 0.8,
                    "top_k": 40
                }
            )
            
            # Extract JSON from response (try multiple methods)
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                try:
                    ai_result = json.loads(json_match.group())
                    
                    score = float(ai_result.get('score', 0.25))  # Default to suspicious (lower)
                    
                    # CRITICAL: Enforce ABSOLUTE rules (AI cannot override these)
                    if debunked_found:
                        score = min(score, 0.15)  # If debunked, max 0.15 (ABSOLUTE)
                    
                    if ai_result.get('is_fake', False):
                        score = min(score, 0.2)  # If AI says fake, max 0.2 (ABSOLUTE)
                    
                    # Check for scam patterns in text (ABSOLUTE CAPS)
                    text_lower = text.lower()
                    scam_phrases = ['free money', 'lottery', 'claim prize', 'forward to claim', 'share to get', 
                                   'government giving', 'pm giving', 'free scheme', 'instant money', 'prize money',
                                   'unclaimed money', 'tax refund', 'reward', 'bonus', 'free cash']
                    if any(phrase in text_lower for phrase in scam_phrases):
                        score = min(score, 0.1)  # Scam = VERY low (ABSOLUTE)
                    
                    urgency_phrases = ['share before deleted', 'forward immediately', 'act now', 'limited time',
                                      'urgent share', 'must forward', 'share now', 'forward to all']
                    if any(phrase in text_lower for phrase in urgency_phrases):
                        score = min(score, 0.2)  # Urgency = very suspicious (ABSOLUTE)
                    
                    # Forward/share manipulation (ABSOLUTE)
                    if any(phrase in text_lower for phrase in ['forward this', 'share this', 'send to', 'tell everyone']):
                        score = min(score, 0.25)  # Viral manipulation = suspicious (ABSOLUTE)
                    
                    # Large numbers with money = SCAM (ABSOLUTE)
                    if re.search(r'\d{4,}', text) and any(word in text_lower for word in ['free', 'money', 'rupees', 'dollars', 'claim']):
                        score = min(score, 0.12)  # Scam with numbers = very low (ABSOLUTE)
                    
                    # Ensure score is reasonable (but respect absolute caps)
                    score = max(0.05, min(0.95, round(score, 2)))
                    
                    red_flags = ai_result.get('red_flags', [])
                    warnings = [f"🚨 {flag}" for flag in red_flags]
                    
                    return {
                        'score': score,
                        'verdict': ai_result.get('verdict', 'AI analysis indicates suspicious content'),
                        'warnings': warnings,
                        'confidence': ai_result.get('confidence', 'medium')
                    }
                except json.JSONDecodeError as e:
                    print(f"⚠️ Failed to parse AI JSON response: {e}")
                    print(f"Response text: {response_text[:500]}")
            else:
                print(f"⚠️ No JSON found in AI response: {response_text[:500]}")
                
        except Exception as e:
            print(f"⚠️ AI verification error: {e}")
            import traceback
            traceback.print_exc()
        
        return {'score': None, 'verdict': None, 'warnings': []}
    
    def _check_fake_patterns(self, text: str) -> tuple:
        """Check for common fake news patterns - ULTRA STRICT VERSION"""
        text_lower = text.lower()
        warnings = []
        score = 0.0
        
        # CRITICAL: Scam/fraud indicators (highest weight - ABSOLUTE RED FLAG)
        scam_patterns = [
            'free money', 'lottery', 'winner', 'claim your prize', 'limited time',
            'act now', 'guaranteed', 'click here', 'congratulations', 'you have won',
            'claim now', 'send to 10 people', 'forward to claim', 'share to get',
            'government giving', 'pm giving', 'free scheme', 'instant money',
            'rupees', 'dollars', 'prize money', 'reward', 'bonus', 'free cash',
            'transfer money', 'bank account', 'aadhar', 'pan card', 'verify account',
            'claim reward', 'unclaimed money', 'tax refund', 'free benefit'
        ]
        found_scam = [p for p in scam_patterns if p in text_lower]
        if found_scam:
            score += 0.8  # EXTREME penalty - SCAM
            warnings.append(f"🚨 SCAM INDICATORS DETECTED: {', '.join(found_scam[:3])}")
        
        # CRITICAL: Urgency/manipulation patterns (VERY HIGH WEIGHT)
        urgency_patterns = [
            'share before deleted', 'forward to everyone', 'spread the word',
            'they dont want you to know', 'banned', 'censored', 'hidden truth',
            'doctors hate this', 'government hiding', 'media hiding', 'secret revealed',
            'forward immediately', 'share now', 'urgent share', 'must forward',
            'share maximum', 'forward to all', 'tell everyone', 'spread this',
            'viral', 'going viral', 'everyone is talking', 'breaking news',
            'urgent', 'important', 'must read', 'must see', 'must share'
        ]
        found_urgency = [p for p in urgency_patterns if p in text_lower]
        if found_urgency:
            score += 0.7  # EXTREME penalty - manipulation
            warnings.append(f"⚠️ MANIPULATION TACTICS: {', '.join(found_urgency[:3])}")
        
        # Sensationalist language
        sensational = [
            'shocking', 'breaking', 'urgent', 'must read', 'must share',
            'viral', 'unbelievable', 'you wont believe', 'secret',
            'exposed', 'revealed', 'truth they hide', 'amazing', 'incredible'
        ]
        found_sensational = [w for w in sensational if w in text_lower]
        if found_sensational:
            score += 0.3
            warnings.append(f"Sensationalist language: {', '.join(found_sensational[:3])}")
        
        # Health misinformation patterns
        health_fake = [
            'miracle cure', 'cancer cured', 'doctors shocked', 'one simple trick',
            'lose weight fast', 'instant cure', 'natural remedy that works',
            'big pharma hiding', 'vaccine causes', 'medical conspiracy'
        ]
        found_health = [p for p in health_fake if p in text_lower]
        if found_health:
            score += 0.4
            warnings.append(f"Health misinformation patterns: {', '.join(found_health[:2])}")
        
        # All caps (screaming)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.4:
            score += 0.2
            warnings.append("Excessive CAPITAL LETTERS (screaming/scam tactic)")
        elif caps_ratio > 0.25:
            score += 0.1
            warnings.append("High use of capital letters")
        
        # Multiple exclamation marks
        exclamation_count = text.count('!')
        if exclamation_count > 5:
            score += 0.2
            warnings.append(f"Excessive exclamation marks ({exclamation_count})")
        elif exclamation_count > 2:
            score += 0.1
            warnings.append("Multiple exclamation marks")
        
        # Question marks (clickbait)
        if text.count('?') > 3:
            score += 0.1
            warnings.append("Multiple question marks (clickbait pattern)")
        
        # Forward chain patterns
        forward_patterns = [
            'forward this', 'send this', 'share this', 'pass this on',
            'tell everyone', 'spread this', 'forward to all'
        ]
        if any(p in text_lower for p in forward_patterns):
            score += 0.3
            warnings.append("Forward/share manipulation detected")
        
        # Numbers/statistics that seem fake
        if re.search(r'\d{4,}', text):  # Very large numbers
            if any(word in text_lower for word in ['free', 'money', 'rupees', 'dollars']):
                score += 0.2
                warnings.append("Suspicious large numbers with money claims")
        
        # Return score (can exceed 1.0 for multiple severe patterns)
        return min(score, 1.2), warnings
    
    def _is_simple_factual_statement(self, text: str) -> bool:
        """Detect if text is a simple factual statement (e.g., 'X is Y)"""
        text_lower = text.lower().strip()
        
        # Remove punctuation for pattern matching
        text_clean = re.sub(r'[^\w\s]', '', text_lower)
        
        # Simple factual patterns (improved to handle usernames, no spaces, etc.)
        factual_patterns = [
            r'^[\w\s]+ is (the|a|an) [\w\s]+ (of|in|at) [\w\s]+$',  # "X is the PM of Y" or "narendramodi is the pm of india"
            r'^[\w\s]+ (is|was|are|were) (the|a|an)? [\w\s]+ (of|in|at) [\w\s]+$',  # More flexible
            r'^[\w\s]+ (is|was|are|were) [\w\s]+$',  # "X is Y"
            r'^[\w\s]+ (holds|held) (the|a) (position|office|post) (of|as) [\w\s]+$',  # "X holds position Y"
            r'^according to [\w\s]+, [\w\s]+$',  # "According to X, Y"
        ]
        
        # Check if it matches simple factual patterns
        for pattern in factual_patterns:
            if re.match(pattern, text_clean):
                return True
        
        # Check for simple statements without manipulation tactics
        if len(text.split()) < 15:  # Short statements
            # No scam/urgency patterns
            scam_words = ['free money', 'lottery', 'claim', 'forward', 'share', 'urgent', 'limited time', 'congratulations', 'you won']
            if not any(word in text_lower for word in scam_words):
                # Contains factual indicators
                factual_indicators = ['is', 'was', 'are', 'were', 'according to', 'said', 'announced', 'pm of', 'president of', 'minister of']
                if any(indicator in text_lower for indicator in factual_indicators):
                    # Check for political/positional facts
                    if any(phrase in text_lower for phrase in ['pm of', 'president of', 'minister of', 'prime minister', 'chief minister']):
                        return True
                    # Check for simple "X is Y" structure
                    if ' is ' in text_lower and len(text.split()) <= 8:
                        return True
                    return True
        
        return False
    
    def _calculate_verification(self, source_cred: dict, fact_checks: list, 
                                cross_refs: list, article: dict) -> dict:
        """Calculate final verification score and verdict - BALANCED VERSION"""
        
        # Start with source credibility
        base_score = source_cred['score']
        confidence = 'medium'
        
        # Use AI verification if available
        article_text = article.get('content', '') + ' ' + article.get('title', '')
        ai_score = None
        if gemini_model and article_text:
            try:
                ai_analysis = self._ai_verify_claim(article_text, fact_checks, [])
                ai_score = ai_analysis.get('score')
            except:
                pass
        
        # Check if it's a simple factual statement (give benefit of doubt)
        is_simple_fact = self._is_simple_factual_statement(article_text)
        if is_simple_fact:
            # Simple facts start at 0.7 (credible unless proven otherwise)
            base_score = max(base_score, 0.7)
        
        # Check content for fake patterns (but don't penalize simple facts too much)
        fake_score, _ = self._check_fake_patterns(article_text)
        has_severe_fake_patterns = fake_score > 0.3
        
        # If it's a simple fact AND has no fake patterns, trust it
        if is_simple_fact and fake_score < 0.1:
            base_score = 0.85  # High confidence for simple facts
        
        # HEAVILY penalize fake patterns (ABSOLUTE)
        if fake_score > 0.7:
            base_score = 0.08  # SCAM
        elif fake_score > 0.5:
            base_score = 0.12  # Very suspicious
        elif fake_score > 0.3:
            base_score = 0.18  # Suspicious
        elif fake_score > 0.1:
            base_score = min(base_score, 0.25)  # Somewhat suspicious
        
        # HEAVILY weight fact-checks (ABSOLUTE PRIORITY)
        debunked_count = 0
        verified_count = 0
        for fc in fact_checks:
            if fc.get('type') not in ['manual_search', 'manual']:
                rating = fc.get('rating', '').lower()
                if rating in ['false', 'fake', 'pants on fire', 'mostly false', 'debunked', 'hoax', 'misleading']:
                    debunked_count += 1
                elif rating in ['true', 'mostly true', 'correct', 'verified']:
                    verified_count += 1
        
        # CRITICAL: Fact-check debunks have ABSOLUTE priority
        if debunked_count >= 2:
            base_score = 0.05  # Multiple debunks = definitely fake (ABSOLUTE)
        elif debunked_count >= 1:
            base_score = min(base_score, 0.15)  # Single debunk = very suspicious (ABSOLUTE)
        
        # Verifications ONLY help if NO fake patterns and NO debunks
        if not has_severe_fake_patterns and debunked_count == 0:
            if verified_count >= 3:
                base_score = min(base_score + 0.2, 0.8)  # Multiple verifications
            elif verified_count >= 2:
                base_score = min(base_score + 0.15, 0.75)  # Two verifications
            elif verified_count >= 1:
                base_score = min(base_score + 0.08, 0.65)  # Single verification (small boost)
        
        # Use AI score if available (but respect fake patterns and debunks)
        if ai_score is not None:
            if ai_score < 0.25:
                base_score = min(base_score, ai_score)  # AI says fake = trust it
            elif has_severe_fake_patterns:
                base_score = min(base_score, 0.25)  # Fake patterns = cap
            elif debunked_count > 0:
                base_score = min(base_score, 0.2)  # Debunked = cap
            else:
                if ai_score < base_score:
                    base_score = (ai_score * 0.7) + (base_score * 0.3)  # Trust AI if stricter
                else:
                    base_score = (ai_score * 0.4) + (base_score * 0.6)  # Be cautious if AI lenient
        
        # Cross-references ONLY help if NO fake patterns and score already decent
        if not has_severe_fake_patterns and debunked_count == 0 and base_score > 0.5:
            if cross_refs and len(cross_refs) >= 3:
                base_score = min(base_score + 0.05, 0.75)  # Small boost only
            elif cross_refs:
                base_score = min(base_score + 0.03, 0.7)
        
        # ABSOLUTE CAPS - fake patterns CANNOT be overcome
        if has_severe_fake_patterns:
            base_score = min(base_score, 0.25)  # MAX 0.25 if fake patterns
        if debunked_count > 0:
            base_score = min(base_score, 0.2)  # MAX 0.2 if debunked
        
        # Clamp score
        score = max(0.05, min(0.95, round(base_score, 2)))
        
        # Determine status
        if score < 0.4:
            status = 'debunked'
        elif score > 0.7:
            status = 'verified'
        else:
            status = 'investigating'
        
        verdict = self._generate_verdict(score, fact_checks, cross_refs)
        
        return {
            'score': score,
            'status': status,
            'verdict': verdict,
            'confidence': confidence
        }
    
    def _generate_verdict(self, score: float, fact_checks: list, cross_refs: list) -> str:
        """Generate human-readable verdict - STRICT VERSION"""
        debunked_count = sum(1 for fc in fact_checks 
                            if fc.get('type') != 'manual_search' and 
                            fc.get('rating', '').lower() in ['false', 'fake', 'debunked', 'hoax'])
        
        verified_count = sum(1 for fc in fact_checks 
                           if fc.get('type') != 'manual_search' and 
                           fc.get('rating', '').lower() in ['true', 'verified', 'correct'])
        
        if score < 0.25:
            return "🚫 STRONG INDICATORS OF MISINFORMATION. This content has been debunked or shows clear signs of being fake. DO NOT SHARE."
        elif score < 0.4:
            if debunked_count > 0:
                return f"🚫 LIKELY FAKE. Fact-checked as false by {debunked_count} source(s). Do NOT share this content."
            else:
                return "⚠️ HIGHLY SUSPICIOUS. Multiple red flags detected. Verify with official sources before sharing."
        elif score < 0.55:
            return "⚠️ QUESTIONABLE CONTENT. This has suspicious elements. Cross-reference with multiple trusted sources before sharing."
        elif score < 0.7:
            if verified_count > 0:
                return "✅ Likely credible, but verify important claims with official sources."
            else:
                return "⚠️ Credibility uncertain. No fact-checks found. Verify with official sources before sharing."
        else:
            if verified_count >= 2:
                return "✅ VERIFIED. Content appears credible and has been verified by multiple fact-check sources."
            elif verified_count >= 1:
                return "✅ Likely credible based on source reputation and fact-check verification."
            else:
                return "✅ Content appears credible based on source reputation, but always verify important news."


# Singleton instances
scraper = NewsScraper()
verifier = NewsVerifier()

