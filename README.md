# WhatsApp Chat Viewer

A web application built using Streamlit to enhance the way you interact with exported WhatsApp chats. This tool provides a tabular view of your chat data while offering rich media handling and search features for a seamless user experience.

### Key Features:

- Rich Media Handling: View images, PDF documents and videos directly within the chat interface.
- Search: Search within chats filtered by month and year to quickly find specific content.
- Customizability: Adjust the number of rows displayed per page, up to a maximum of 100 rows.
- Access URLs

GitHub repository: 
	https://github.com/SristiAH/WhatsApp_Chat_Viewer

## Installation

To set up your Python environment to run the project, follow these steps:

1. Set up the project directory structure as shown below.
2. Open a terminal and navigate to the project directory.
3. Create a virtual environment.
4. Install the required packages:
```bash
pip install -r requirements.txt
```

## Setting up Python virtual environment (On Linux)

I. Open a terminal and make sure you have Python 3 installed. You can check your Python version by running the following command:

	python3 --version

II. Install the venv module, which is used to create virtual environments. You can do this by running the following command:

	sudo apt-get install python3-venv

III. Navigate to the directory where you want to create your virtual environment.

IV. Run the following command to create a virtual environment with the name myenv:

	python3 -m venv myenv

V. Activate the virtual environment by running the following command:

	source myenv/bin/activate

Your virtual environment is now ready to use. You can install packages and run Python scripts inside the virtual environment without affecting the packages and scripts outside of it. To deactivate the virtual environment, run the deactivate command.

## Usage

To run the application:

1. Open a terminal or command prompt.
2. Navigate to the project directory.
3. Activate your virtual environment:  (On Linux)

```bash
source myenv/bin/activate       
``` 
4. Run the following command:
```bash
streamlit run chat_viewer_updated.py
```

**Note:** The parent folder of the virtual environment folder should not be modified.

## Directory structure

```bash
~/Directory
├── chat_viewer_updated.py     # Main script to run the application 
├── Doc
│   └── PDF documents              
├── image
│   └── images
├── video
│   └── mp4 files             
├── custom.txt	               # Default text file that is loaded on running the app (exported WhatsApp chat)
└── requirements.txt           # Dependencies 
```

## License

This software is released under MIT license.

### Author

*Sristi A H* - [GitHub Profile](https://github.com/SristiAH)
