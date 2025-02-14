async def main():
    render_header()

    # Get URLs from bulk upload or single input
    urls = render_upload_section()
    single_url = st.text_input("Or analyze a single URL:", placeholder="https://example.com")

    if single_url:
        urls = [single_url]

    # Centered submit button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button("🚀 Analyze Websites")

    if urls and analyze_button:
        invalid_urls = [url for url in urls if not validate_url(url)]
        if invalid_urls:
            st.error(f"Invalid URLs found: {', '.join(invalid_urls)}")
            return

        with st.spinner("🔍 Analyzing websites..."):
            try:
                # Initialize API client
                api_client = PageSpeedInsightsAPI()
                all_results = []

                # Analyze URLs concurrently
                tasks = [analyze_url(api_client, url) for url in urls]
                results = await asyncio.gather(*tasks)

                # Filter out None results (failed analyses)
                all_results = [result for result in results if result is not None]

                # Display results
                for result in all_results:
                    with st.expander(f"Analyzing {result['url']}", expanded=True):
                        display_metrics(result['desktop'], result['mobile'])

                if all_results:
                    st.success(f"✅ Analysis completed for {len(all_results)} URLs")

                    # Export options
                    st.subheader("Export Results")
                    export_format = st.selectbox("Choose export format:", ['json', 'csv', 'excel'])

                    export_data = export_results(all_results, export_format)

                    if export_format == 'json':
                        st.download_button(
                            "📥 Download JSON Report",
                            export_data,
                            file_name="seo_audit_results.json",
                            mime="application/json"
                        )
                    elif export_format == 'csv':
                        st.download_button(
                            "📥 Download CSV Report",
                            export_data,
                            file_name="seo_audit_results.csv",
                            mime="text/csv"
                        )
                    else:  # excel
                        st.download_button(
                            "📥 Download Excel Report",
                            export_data,
                            file_name="seo_audit_results.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

            except Exception as e:
                error_msg = str(e)
                if "API key not found" in error_msg:
                    st.error("⚠️ Configuration Error: The PageSpeed Insights API key is not properly set up. Please contact support.")
                elif "Failed to fetch metrics" in error_msg:
                    st.error("🌐 Network Error: Unable to fetch data from Google PageSpeed Insights. Please try again later.")
                elif "Invalid API response" in error_msg:
                    st.error("🚫 API Error: Received invalid response from PageSpeed Insights. Please try again later.")
                else:
                    st.error(f"❌ An unexpected error occurred: {error_msg}")

                # Log the full error for debugging
                st.write("Debug information:")
                st.code(traceback.format_exc())