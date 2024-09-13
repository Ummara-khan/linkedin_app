import streamlit as st
import PIL.Image
import re

# Page configuration
st.set_page_config(
    page_title="LinkedIn Profile Photo Analyzer",
    page_icon="👩‍💼",
    layout="wide"
)

# Subheader
st.subheader(":blue[LinkedIn] Profile Photo Analyzer", divider="gray")
st.caption("Powered by Gemini Pro Vision")

# Use the hardcoded API key
api_key = "AIzaSyBRbtq6js1btney8LzswW0Npo_fxiQ09AE"

col1, col2 = st.columns(spec=[0.4, 0.6], gap="medium")

img = None  # Initialize the image

with col1:
    with st.container(border=True):
        img_ = st.file_uploader(
            label=":red[Upload your image]",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=False,
            key="image0",
            help="Upload your image to generate a description"
        )

        # Show the image
        if img_ is not None:
            st.image(img_, caption="Uploaded Image", use_column_width=True)

            # Save the image with PIL.Image
            img = PIL.Image.open(img_)

def get_analysis(prompt, image):
    import google.generativeai as genai
    genai.configure(api_key=api_key)

    # Set up the model
    generation_config = {
        "temperature": 0.9,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 5000,
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
    ]

   # Update the model to gemini-1.5-flash
    model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    response = model.generate_content([prompt, image])

    return response.text

role = """
You are an expert AI tasked with evaluating LinkedIn profile photos and providing detailed feedback on their quality. Your feedback should be professional, constructive, and aimed at helping users improve their profile images.
"""

instructions = """
You will receive an image file of a LinkedIn profile photo.

Your task is to provide a structured report analyzing the image based on the following criteria:

Resolution and Clarity:

Evaluate the resolution and clarity of the image. Determine if the image is blurry or pixelated, which may affect the visibility of features. If the image lacks clarity, suggest the user upload a higher-resolution photo. (Include a confidence score for this assessment.)

Professional Appearance:

Assess the attire of the person in the image. Describe what they are wearing and whether it is suitable for a professional setting. Also, evaluate the background. If the background is simple and uncluttered, mention that it helps keep the focus on the person. If the attire or background is unsuitable, recommend more formal clothing or a plain background, respectively. (Include a confidence score for this assessment.)

Face Visibility:

Examine how clearly the person’s face is visible. If the face is unobstructed and clearly visible, note this. If the face is partially covered by objects or hair, or if the person is looking away, provide feedback and suggest looking directly into the camera for a stronger connection. (Include a confidence score for this assessment.)

Appropriate Expression:

Analyze the person’s expression. If the expression is friendly and approachable, acknowledge this. If the expression appears overly serious or unprofessional, suggest a more relaxed and natural smile. (Include a confidence score for this assessment.)

Filters and Distortions:

Review any filters or distortions applied to the image. If the image appears natural, note this. If it is excessively filtered or retouched, recommend using a more natural-looking photo. (Include a confidence score for this assessment.)

Single Person and No Pets:

Identify the number of people and pets in the image. If only the user is present, confirm this. If there are multiple people or pets, suggest cropping the image to eliminate distractions. (Include a confidence score for this assessment.)

Final review:

Conclude with a summary of whether the image is suitable for a LinkedIn profile photo and provide the rationale for your assessment.
"""

output_format = """
Your report should be structured like shown in triple backticks below:

1. Resolution and Clarity:\n[description] (confidence: [confidence score]%)

2. Professional Appearance:\n[description] (confidence: [confidence score]%)

3. Face Visibility:\n[description] (confidence: [confidence score]%)

4. Appropriate Expression:\n[description] (confidence: [confidence score]%)

5. Filters and Distortions:\n[description] (confidence: [confidence score]%)

6. Single Person and No Pets:\n[description] (confidence: [confidence score]%)

Final review:\n[your review]

less
Copy code

You should also provide a confidence score for each assessment, ranging from 0 to 100.

Don't copy the above text. Write your own report.

And always keep your output in this format.

For example:

**1. Resolution and Clarity:**\n[Your description and analysis.] (confidence: [score here]%)

**2. Professional Appearance:**\n[Your description and analysis.] (confidence: [socre here]%)

**3. Face Visibility:**\n[Your description and analysis.] (confidence: [score her]%)

**4. Appropriate Expression:**\n[Your description and analysis.] (confidence: [score here]%)

**5. Filters and Distortions:**\n[Your description and analysis.] (confidence: [score here]%)

**6. Single Person and No Pets:**\n[Your description and analysis.] (confidence: [score here]%)

**Final review:**\n[Your review]
"""

prompt = role + instructions + output_format

image_parts = [    {        "mime_type": "image/jpeg",        "data": img    }]

with col2:
    with st.container(border=True):
        st.markdown(":grey[Click the button to analyze the image]")
        analyze_button = st.button(
            "ANALYZE",
            type="primary",
            disabled=not img_,
            help="Analyze the image",
            use_container_width=True
        )

        if analyze_button:
            # Show spinner while generating
            with st.spinner("Analyzing..."):

                try:
                    # Get the analysis
                    analysis = get_analysis(prompt, img)
                except Exception as e:
                    st.error(f"An error occurred: {e}")

                else:
                    # Find all the headings that are enclosed in ** **
                    headings = re.findall(r"\*\*(.*?)\*\*", analysis)

                    # Find all the features that are after ** and before (confidence
                    features = re.findall(r"\*\*.*?\*\*\n(.*?)\s\(", analysis)

                    # Find all the confidence scores that are after (confidence: and before %)
                    confidence_scores = re.findall(r"\(confidence: (.*?)\%\)", analysis)

                    # Find the final review which is after the last confidence score like this:
                    # (confidence: 50%)\n\n(.*?)
                    final_review = re.findall(r"\*\*Final review:\*\*\n(.*?)$", analysis)[0]

                    for i in range(6):
                        st.divider()
                        st.markdown(f"**{headings[i]}**\n\n{features[i]}")
                        # Show progress bar
                        st.progress(int(confidence_scores[i]), text=f"confidence score: {confidence_scores[i]}")

                    st.divider()
                    st.markdown(f"**Final review:**\n{final_review}")