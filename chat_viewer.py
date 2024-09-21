# Month and year filtering with comments
import streamlit as st    # For building the web app
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode    # For creating interactive tables
from st_aggrid.shared import JsCode    # To embed JavaScript in tables
import pandas as pd    # Work with tabular data
import os    # Checking existence of files
import base64    # For encoding files 
import re    # For text pattern matching with regex 

# Set the page layout to wide 
st.set_page_config(layout="wide")

file_name = st.sidebar.text_input("Enter the text file: ", value="custom.txt", key="file_name")

if not os.path.isfile(file_name):
    st.warning("File doesn't exist")
    st.stop()  

file = open(file_name, 'r')

chat = pd.DataFrame(columns=['SERIAL NO.', 'DATE', 'TIME', 'MESSAGE', 'image_path', 'DOCUMENT', 'VIDEO', 'URL'])

# Function to extract dates and their corresponding indices from the text file
def extract_dates(file_path):
    with open(file_path, 'r') as file:
        dates_indices = []
        index = 0
        for line in file:
            if len(line) >= 14 and line[2] == '/' and line[5] == '/':    # Check if the line contains a date
                date = line[:10]  
                dates_indices.append((date, index))  
            index += 1  
    return dates_indices  

def get_range_for_month_year(file_path, target_month, target_year):
    dates_indices = extract_dates(file_path)  # Extract date and index tuples from the file
    start_index, end_index = None, None  
    
    found_matching_date = False  # Flag to indicate if we have found a matching month/year
    
    for idx, (date, i) in enumerate(dates_indices):
        day, month, year = date.split('/')  
        
        if month == target_month and year == target_year:
            if start_index is None:
                start_index = i  
            end_index = i  # Update the end index on every match
            found_matching_date = True
        
        # If we have already found a matching month/year, check the next date
        elif found_matching_date:
            break

    if start_index is None:
        # No matching month and year found
        return None, None, f"No data found for {target_month}/{target_year}"

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for j in range(end_index + 1, len(lines)):
            if len(lines[j]) >= 14 and lines[j][2] == '/' and lines[j][5] == '/':
                # Stop when a new date is encountered
                break
            # If no new date is found, extend the range to include this line
            end_index = j

    return start_index, end_index, None  

# Function to process chat data between range of indices for the filtered month and year
def process_chat(start_row, end_row, file, chat):
    a = ''
    b = ''
    c = ''
    i = -1  
    for pos, data in enumerate(file):
        if pos < start_row:
            continue  # Skip lines until reaching the start row

        if not i == -1:
            chat.loc[i, 'SERIAL NO.'] = i + 1
            chat.loc[i, 'DATE'] = a
            chat.loc[i, 'TIME'] = b
            chat.loc[i, 'MESSAGE'] = c

        if pos > end_row:
            break  

        i = i + 1  

        chat.loc[i, 'image_path'] = ' '
        chat.loc[i, 'DOCUMENT'] = ' '
        chat.loc[i, 'VIDEO'] = ' '
        chat.loc[i, 'URL'] = ' '

        # Handle lines that are part of a previous message
        if len(data) < 14:
            a = chat.loc[i-1, 'DATE']  
            b = chat.loc[i-1, 'TIME'] 
            i -= 1  
            c += data  
            continue

        if data[2] == '/' and data[5] == '/':
            a = data[0:10]    # Extract date
        else:
            a = ''

        for word in data.split(' '):
            for ext in ['jpg', 'jpeg', 'png', 'gif']:
                if word.endswith(ext):    # Check for image files
                    imagepath = 'image/' + word
                    if os.path.isfile(imagepath):
                        chat.loc[i, 'image_path'] = imagepath  
                    else:
                        chat.loc[i, 'image_path'] = word + ' not found'

            if word.endswith('.pdf'):    # Check for PDF files
                filepath = 'Doc/' + word
                if os.path.isfile(filepath):
                    chat.loc[i, 'DOCUMENT'] = filepath  
                else:
                    chat.loc[i, 'DOCUMENT'] = word + ' not found'

            if word.endswith('.mp4'):    # Check for video files
                videopath = 'video/' + word
                if os.path.isfile(videopath):
                    chat.loc[i, 'VIDEO'] = videopath  
                else:
                    chat.loc[i, 'VIDEO'] = word + ' not found'

            if word.startswith('http'):     # Check for URLs
                link = word
                name=re.search("https?://.+", link)
                if name:
                    chat.loc[i,'URL'] = link

        if data[11] == " " and data[14] == ":":
            b = data[12:17]  # Extract time
        else:
            b = ''

        if a != '' and b != '':
            c = data[20:]  # Extract message
        else:
            # Continue the message from the previous row
            a = chat.loc[i-1, 'DATE']
            b = chat.loc[i-1, 'TIME']
            i -= 1
            c += data

    # After loop ends, process the final row
    chat.loc[i, 'SERIAL NO.'] = i + 1
    chat.loc[i, 'DATE'] = a
    chat.loc[i, 'TIME'] = b
    chat.loc[i, 'MESSAGE'] = c

    return chat  

# Read and encode a file in Base64 format
def read_and_encode_file(file_path, file_type):
    try:
        with open(file_path, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode()
            if file_path.endswith('mp4'):
                return f'data:{file_type};base64,{encoded}'  # Return video URL for .mp4 files
            else:
                return encoded  # Return encoded string for other file types
    except:
        return ''  

# JavaScript code to show images in the grid
ShowImage = JsCode("""
    class ShowImage {
        init(params) {
            var img = document.createElement('img');
            img.src = params.data.IMAGE_DATA_URL || '';
            img.style.maxWidth = img.style.maxHeight = '100%';
            this.eGui = document.createElement('span');
            this.eGui.appendChild(img);
        }
        getGui() {
            return this.eGui;
        }
    }
""")

# JavaScript function to handle image clicks and open them in a new window
clicked_image_cell = """
function(params){
    var imgSrc = params.data.IMAGE_DATA_URL;  
    var extension = imgSrc.substring(imgSrc.indexOf('/')+1, imgSrc.indexOf(';base64'));
    if (imgSrc && imgSrc !== '') {
        var win = window.open("", "Image", "height=600, width=800, left=100, top=100");
        win.document.write("<img src='" + imgSrc + "' style='width:auto;height:auto;'><br>"+
            "<a href='" + imgSrc + "' download='downloaded_image." + extension + "'>Download Image</a>");
        win.focus();
    }
}
"""

# JavaScript function to handle PDF clicks and open them in a new window
clicked_pdf_cell = """
function(params) {
    var pdfUrl = params.data.PDF_URL; 
    if (pdfUrl && pdfUrl !== '') {
        var win = window.open("", "PDF", "height=600, width=800, left=100, top=100");
        win.document.write("<a href='" + pdfUrl + "' download='document.pdf'>Download PDF</a><br>");
        win.document.write("<iframe src='" + pdfUrl + "' width='100%' height='100%'></iframe>");
        win.focus();
    }
}
"""

# JavaScript function to handle video clicks and open them in a new window
clicked_video_cell = """
function(params) {
    var videoUrl = params.data.VIDEO_URL;
    if (videoUrl && videoUrl !== '') {
        var win = window.open("", "Video", "height=600, width=800, left=100, top=100");
        win.document.write("<video controls style='width:100%; height:auto;'>"+
            "<source src='" + videoUrl + "' type='video/mp4'>"+
            "Your browser does not support the video tag."+
            "</video><br><a href='" + videoUrl + "' download>Download Video</a>");
        win.focus();
    }
}
"""

# Function to process data and encode file URLs for images, documents, and videos
def process_data_urls(chat_df):
    for i, row in chat_df.iterrows():
        # Check if image file exists and encode it
        if os.path.isfile(row['image_path']):
            imgExtn = row['image_path'].split('.')[-1].lower()
            if imgExtn in ['jpg', 'jpeg', 'png', 'gif']:
                image_data = read_and_encode_file(row['image_path'], f'image/{imgExtn}')
                chat_df.at[i, 'IMAGE_DATA_URL'] = f'data:image/{imgExtn};base64,{image_data}'
        else:
            chat_df.at[i, 'IMAGE_DATA_URL'] = ''  

        # Check if document (PDF) exists and encode it
        if os.path.isfile(row['DOCUMENT']):
            pdf_data = read_and_encode_file(row['DOCUMENT'], 'application/pdf')
            chat_df.at[i, 'PDF_URL'] = f'data:application/pdf;base64,{pdf_data}'
        else:
            chat_df.at[i, 'PDF_URL'] = ''

        # Check if video file exists and encode it
        if os.path.isfile(row['VIDEO']):
            video_data = read_and_encode_file(row['VIDEO'], 'video/mp4')
            chat_df.at[i, 'VIDEO_URL'] = video_data
        else:
            chat_df.at[i, 'VIDEO_URL'] = ''

    return chat_df  

# Extract dates and their indices from the file
dates_indices = extract_dates(file_name)

# Create GridOptionsBuilder for the AgGrid table
gb = GridOptionsBuilder.from_dataframe(chat)
gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)  # Enable pagination 

gb.configure_column('MESSAGE', wrapText=True, autoHeight=True)
gb.configure_column('IMAGE', cellRenderer=ShowImage, onCellClicked=JsCode(clicked_image_cell))
gb.configure_column('DOCUMENT', onCellClicked=JsCode(clicked_pdf_cell))
gb.configure_column('VIDEO', onCellClicked=JsCode(clicked_video_cell))

gb.configure_columns(['IMAGE_DATA_URL', 'PDF_URL', 'VIDEO_URL', 'image_path'], hide=True)

# Configure URL column to render clickable links
gb.configure_column(
    "URL",
    headerName="URL",
    cellRenderer=JsCode("""
        class UrlCellRenderer {
          init(params) {
            if (params.value && params.value.startsWith('http')) {
                this.eGui = document.createElement('a');
                this.eGui.innerText = params.value;  // Display custom text for the link
                this.eGui.setAttribute('href', params.value);
                this.eGui.setAttribute('style', "text-decoration:none; color:blue;");
                this.eGui.setAttribute('target', "_blank");
            }
          }
          getGui() {
            return this.eGui;
          }
        }
    """), type='link'
)

st.sidebar.title("Filter by Month and Year")

# Dropdown to select a month from the sidebar
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
selected_month = st.sidebar.selectbox("Select Month", months, index=5)  # Default to June

# Number input to select a year from the sidebar
selected_year = st.sidebar.number_input("Select Year", min_value=2024, max_value=2100, value=2024, step=1)

# Get the start and end indices for the selected month and year
start_index, end_index, message = get_range_for_month_year(file_name, selected_month, str(selected_year))

# If valid data is found, process the chat between the given indices
if not message:
    process_chat(start_index, end_index, file, chat)

# Process and encode file data URLs for images, documents, and videos
chat = process_data_urls(chat)

# Build the grid options with the configurations
grid_options = gb.build()
grid_options['rowHeight'] = 100  

# Text input for searching within the chat data
text_search = st.text_input("Search", value="")

# Filter the chat based on search input (searches in DATE, TIME, and MESSAGE columns)
if text_search:
    m1 = chat['DATE'].str.contains(text_search, case=False)
    m2 = chat['TIME'].str.contains(text_search, case=False)
    m3 = chat['MESSAGE'].str.contains(text_search, case=False)
    chat = chat[m1 | m2 | m3]

# Display the chat data in an interactive AgGrid table
AgGrid(
    chat,
    gridOptions=grid_options,
    height=600,
    allow_unsafe_jscode=True,  
    fit_columns_on_grid_load=False,
    use_container_width=True,
    updateMode=GridUpdateMode.VALUE_CHANGED
)

if not message:
    chat.drop(['IMAGE_DATA_URL', 'PDF_URL', 'VIDEO_URL', 'image_path'], axis=1, inplace=True)
