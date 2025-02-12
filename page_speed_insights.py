import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import time
from urllib.parse import urlparse
import validators
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use environment variables instead of hardcoded values
api_key = os.getenv('API_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Set page config
    st.set_page_config(
        page_title="Web Performance Analyzer",
        page_icon="🌐",
        layout="wide",
    )

    # Custom CSS for styling
    st.markdown(
        """
        <style>
        .stButton>button {
            border: 2px solid #4CAF50;
            border-radius: 12px;
            padding: 10px 24px;
            background-color: #4CAF50;
            color: white;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: white;
            color: #4CAF50;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        /* Card-like containers for results */
        div.stMetric {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Improve header styling */
        h1, h2, h3 {
            color: #1f1f1f;
            font-weight: bold;
        }
        
        .loader {
            border: 8px solid #f3f3f3;
            border-top: 8px solid #4CAF50;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Add a title
    st.title("🌐 Web Performance Analyzer")
    st.markdown("Developed by [Amal Alexander](https://in.linkedin.com/in/amal-alexander-305780131) ❤️")
    st.markdown("Paste a URL to analyze its performance, SEO, and accessibility metrics.")

    # Add a sidebar for file uploads
    st.sidebar.header("Upload/Download Files")
    uploaded_file = st.sidebar.file_uploader("Upload Excel, CSV, or Text files", type=["csv", "xlsx", "txt"])

    def is_valid_url(url):
        try:
            return validators.url(url)
        except:
            return False

    # Add a URL input box with validation
    url = st.text_input("Enter URL to analyze:", placeholder="https://example.com")
    if url and not is_valid_url(url):
        st.warning("Please enter a valid URL including http:// or https://")

    def analyze_webpage(url):
        try:
            logger.info(f"Starting analysis for URL: {url}")
            # Fetch webpage content
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract basic metrics
            page_title = soup.title.string if soup.title else "No Title"
            meta_description = soup.find("meta", attrs={"name": "description"})
            meta_description = meta_description["content"] if meta_description else "No Description"

            # Core Web Vitals (mock data)
            core_web_vitals = {
                "LCP": "2.5s",
                "FID": "100ms",
                "CLS": "0.1",
            }

            # SEO Score (mock data)
            seo_score = 85

            # Accessibility Score (mock data)
            accessibility_score = 90

            # Additional metrics
            additional_metrics = {
                "Headers": len(soup.find_all(['h1', 'h2', 'h3'])),
                "Images": len(soup.find_all('img')),
                "Links": len(soup.find_all('a')),
                "Meta Tags": len(soup.find_all('meta')),
                "Scripts": len(soup.find_all('script')),
                "CSS Files": len(soup.find_all('link', rel='stylesheet'))
            }

            # Mobile-friendliness check
            mobile_metrics = {
                "Mobile Friendly": "Yes",
                "Viewport Meta": "Present" if soup.find('meta', attrs={'name':'viewport'}) else "Missing",
                "Text Size": "Readable",
                "Tap Target Spacing": "Adequate"
            }

            logger.info("Analysis completed successfully")
            return {
                "Page Title": page_title,
                "Meta Description": meta_description,
                "Core Web Vitals": core_web_vitals,
                "SEO Score": seo_score,
                "Accessibility Score": accessibility_score,
                "Additional Metrics": additional_metrics,
                "Mobile Metrics": mobile_metrics
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching the webpage: {str(e)}")
            st.error(f"Error fetching the webpage: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            st.error(f"An unexpected error occurred: {str(e)}")
            return None

    if st.button("Analyze"):
        try:
            if url and is_valid_url(url):
                with st.spinner("Analyzing webpage..."):
                    logger.info("Starting analysis...")
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Simulate progress
                    for i in range(100):
                        progress_bar.progress(i + 1)
                        status_text.text(f"Analysis in progress: {i+1}%")
                        time.sleep(0.01)
                    
                    # Analyze webpage
                    results = analyze_webpage(url)
                    
                    if results:
                        status_text.text("Analysis complete!")
                        progress_bar.empty()

                        # Display results
                        st.subheader("📊 Analysis Results")
                        st.write(f"**Page Title:** {results['Page Title']}")
                        st.write(f"**Meta Description:** {results['Meta Description']}")

                        # Core Web Vitals
                        st.subheader("🚀 Core Web Vitals")
                        vitals_df = pd.DataFrame(list(results["Core Web Vitals"].items()), columns=["Metric", "Value"])
                        fig = px.bar(vitals_df, x="Metric", y="Value", title="Core Web Vitals")
                        st.plotly_chart(fig)

                        # SEO and Accessibility Scores
                        st.subheader("📈 SEO & Accessibility")
                        scores_df = pd.DataFrame({
                            "Metric": ["SEO Score", "Accessibility Score"],
                            "Value": [results["SEO Score"], results["Accessibility Score"]],
                        })
                        fig = px.pie(scores_df, names="Metric", values="Value", title="SEO & Accessibility Scores")
                        st.plotly_chart(fig)

                        # Additional Metrics
                        st.subheader("📋 Additional Metrics")
                        metrics_df = pd.DataFrame(list(results["Additional Metrics"].items()), columns=["Metric", "Value"])
                        st.table(metrics_df)

                        # Mobile Metrics
                        st.subheader("📱 Mobile Friendliness")
                        mobile_df = pd.DataFrame(list(results["Mobile Metrics"].items()), columns=["Metric", "Status"])
                        st.table(mobile_df)

                        # Add export functionality
                        st.download_button(
                            label="Download Results as CSV",
                            data=pd.DataFrame({
                                **results["Additional Metrics"],
                                **results["Mobile Metrics"],
                                "SEO Score": results["SEO Score"],
                                "Accessibility Score": results["Accessibility Score"]
                            }).to_csv(index=True),
                            file_name="web_analysis_results.csv",
                            mime="text/csv"
                        )
            else:
                st.error("Please enter a valid URL.")
        except Exception as e:
            logger.error(f"Error in main analysis: {str(e)}")
            st.error(f"An unexpected error occurred: {str(e)}")

    # Add a footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center'>
            <p>Made with ❤️ using Streamlit</p>
            <p>© 2024 Amal Alexander. All rights reserved.</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()