import json
import xml.etree.ElementTree as ET

# def jsonToOpml(input_file, output_file):
#     # Read the input JSON file
#     with open(input_file, 'r') as f:
#         data = json.load(f)
    
#     # Create the root element for OPML
#     opml = ET.Element("opml", version="2.0")
#     head = ET.SubElement(opml, "head")
#     title = ET.SubElement(head, "title")
#     title.text = "YouTube Subscriptions"

#     body = ET.SubElement(opml, "body")
    
#     # Iterate over subscriptions and create OPML outline elements
#     for subscription in data.get('subscriptions', []):
#         channel_name = subscription.get('name')
#         channel_url = subscription.get('url')
        
#         # Extract the channel_id from the URL
#         channel_id = channel_url.split('/')[-1]
#         rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        
#         # Create outline element
#         outline = ET.SubElement(body, "outline", {
#             "text": channel_name,
#             "title": channel_name,
#             "type": "rss",
#             "xmlUrl": rss_url
#         })
    
#     # Convert the tree to a string
#     opml_str = ET.tostring(opml, encoding='utf-8', method='xml')
    
#     # Write the OPML string to the output file
#     with open(output_file, 'wb') as f:
#         f.write(opml_str)

# # Example usage
# jsonToOpml("opml.json", "output.opml")



import requests

def post_request_to_readability_server():
    # Define the endpoint and payload
    url = "http://alma:3525/"
    payload = {"url": "https://indianexpress.com/article/upsc-current-affairs/upsc-essentials/isros-aditya-l1-payloads-significance-and-impact-on-day-to-day-life-9546389/"}

    # Define headers
    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Make the POST request
        response = requests.post(url, json=payload, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            response_data = response.json()

            # Check if 'content' key exists in the JSON response
            if 'content' in response_data:
                # Get the HTML content
                html_content = response_data['content']

                # Save the content as an HTML file
                with open('response.html', 'w', encoding='utf-8') as html_file:
                    html_file.write(html_content)
                print("HTML content saved to 'response.html'")
            else:
                print("The key 'content' was not found in the response.")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        # Print any error that occurs during the request
        print("An error occurred:", e)

# Call the function
post_request_to_readability_server()