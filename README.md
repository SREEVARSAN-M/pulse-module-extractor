Pulse – Module Extraction AI Agent



Overview

This project is an AI-powered Streamlit application that extracts modules and submodules from documentation-based help websites. It processes the structural hierarchy of documentation pages and generates content-grounded descriptions for each module and submodule.

The tool is designed to help product teams and analysts quickly understand how a product’s documentation is organized and what functionality each part represents.



Features

Accepts one or more documentation URLs

Extracts meaningful content while ignoring navigation noise

Infers modules from top-level documentation sections

Infers submodules from nested documentation headings

Generates detailed descriptions using content-based AI summarization

Outputs structured JSON

Interactive Streamlit UI with download support

Architecture & Approach

High-level pipeline:

URL validation and HTML fetching

Content cleaning (removal of navigation, footer, scripts)

Structural parsing using heading hierarchy (H1 → H2 → H3)

Module and submodule inference

AI-assisted description generation based strictly on extracted content

Structured JSON output and UI visualization

The system prioritizes documentation structure and hierarchy rather than keyword matching, ensuring logical grouping and consistency.


Example Output Structure

[
  {
    "module": "Account Management",
    "Description": "Includes tools and settings related to managing user accounts.",
    "Submodules": {
      "Change Password": "Explains how users can update their account password.",
      "Deactivate Account": "Details steps to temporarily disable an account."
    }
  }
]


Assumptions

Documentation pages follow standard HTML heading structure

H1 tags represent major modules

H2/H3 tags represent submodules

Only meaningful textual content is processed

Crawling depth is intentionally limited to maintain efficiency

Limitations

Deep recursive crawling is not enabled

JavaScript-rendered documentation pages are not supported

Description accuracy depends on documentation clarity

Semantic merging of highly similar modules is limited

Future Enhancements

Support for multiple documentation sources simultaneously

Confidence scores for extracted modules

Shallow recursive crawling with link filtering

Caching of previously processed pages

REST API version of the extractor




How to Run
pip install -r requirements.txt
streamlit run app/app.py




Screenshots and sample outputs are included to demonstrate:

URL input

Successful extraction

Structured JSON output
