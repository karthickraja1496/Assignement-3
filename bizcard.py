import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import mysql.connector 
from PIL import Image
import os
import re

# SETTING PAGE CONFIGURATIONS
st.markdown("<h1 style='text-align: center; color: red;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)


# CREATING OPTION MENU
selected = option_menu(None, ["Home","Upload & Extract","View & Modify"], 
                       icons=["house","cloud-upload","pencil-square"],
                       default_index=0,
                       orientation="horizontal")

# INITIALIZING THE EasyOCR READER
reader = easyocr.Reader(['en'])

# Connect to the database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bizcardx_db"  # Specify the database name
)

mycursor = mydb.cursor(buffered=True)

# TABLE CREATION
mycursor.execute('''CREATE TABLE IF NOT EXISTS business_card
                   (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    Company_Name TEXT,
                    Name TEXT,
                    Designation TEXT,
                    Mobile_Number VARCHAR(50),
                    Email TEXT,
                    Website TEXT,
                    Area TEXT,
                    City TEXT,
                    State TEXT,
                    Pin_Code VARCHAR(10),
                    Image LONGBLOB
                    )''')

# HOME MENU
if selected == "Home":
        st.markdown("#### :green[*Technologies Used :*] Python, Pandas, SQL, Easy OCR, Streamlit")
        st.markdown("#### :green[*Overview :*] In this Streamlit app you can upload an image of a business card and extract information using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the Business Card.")
        
        
# UPLOAD AND EXTRACT MENU
if selected == "Upload & Extract":
    st.markdown("### Upload a Business Card")
    uploaded_card = st.file_uploader("upload here",label_visibility="collapsed",type=["png","jpeg","jpg"])
        
    if uploaded_card is not None:
        
        def save_card(uploaded_card):
            target_directory = "uploaded_cards"
            
            if not os.path.exists(target_directory):
                os.makedirs(target_directory)
            with open(os.path.join(target_directory, uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())

    
        save_card(uploaded_card)
        
        # DISPLAYING THE UPLOADED CARD
        col1,col2 = st.columns(2,gap="large")
        with col1:
            st.markdown("#     ")
            st.markdown("#     ")
            st.markdown("### You have uploaded the card")
            st.image(uploaded_card)
        #easy OCR
        saved_img = os.getcwd()+ "\\" + "uploaded_cards"+ "\\"+ uploaded_card.name
        result = reader.readtext(saved_img,detail = 0,paragraph=False)
        
        # CONVERTING IMAGE TO BINARY TO UPLOAD TO SQL DATABASE
        def img_to_binary(file):
            # Convert image data to binary format
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData
        
        data = {"Company_Name" : [],
                "Name" : [],
                "Designation" : [],
                "Mobile_Number" :[],
                "Email" : [],
                "Website" : [],
                "Area" : [],
                "City" : [],
                "State" : [],
                "Pin_Code" : [],
                "Image" : img_to_binary(saved_img)
            }

        def get_data(res):
            for ind,i in enumerate(res):

                # To get WEBSITE_URL
                if "www " in i.lower() or "www." in i.lower():
                    data["Website"].append(i)
                elif "WWW" in i:
                    data["Website"] = res[4] +"." + res[5]

                # To get EMAIL ID
                elif "@" in i:
                    data["Email"].append(i)

                # To get MOBILE NUMBER
                elif "-" in i:
                    data["Mobile_Number"].append(i)
                    if len(data["Mobile_Number"]) ==2:
                        data["Mobile_Number"] = " & ".join(data["Mobile_Number"])

                # To get COMPANY NAME  
                elif ind == len(res)-1:
                    data["Company_Name"].append(i)

                # To get CARD HOLDER NAME
                elif ind == 0:
                    data["Name"].append(i)

                # To get DESIGNATION
                elif ind == 1:
                    data["Designation"].append(i)

                # To get AREA
                if re.findall('^[0-9].+, [a-zA-Z]+',i):
                    data["Area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+',i):
                    data["Area"].append(i)

                # To get CITY NAME
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*',i)
                if match1:
                    data["City"].append(match1[0])
                elif match2:
                    data["City"].append(match2[0])
                elif match3:
                    data["City"].append(match3[0])

                # To get STATE
                state_match = re.findall('[a-zA-Z]{9} +[0-9]',i)
                if state_match:
                    data["State"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);',i):
                    data["State"].append(i.split()[-1])
                if len(data["State"])== 2:
                    data["State"].pop(0)

                # To get PINCODE        
                if len(i)>=6 and i.isdigit():
                    data["Pin_Code"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]',i):
                    data["Pin_Code"].append(i[10:])
        get_data(result)
        
        #FUNCTION TO CREATE DATAFRAME
        def create_df(data):
            df = pd.DataFrame(data)
            return df
        df = create_df(data)
        st.success("#### Data Extracted!")
        st.write(df)
        
        if st.button("Upload to Database"):
            for i,row in df.iterrows():
                #here %S means string values 
                sql = """INSERT INTO business_card(Company_Name,Name,Designation,Mobile_Number,Email,Website,Area,City,State,Pin_Code,Image)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                mycursor.execute(sql, tuple(row))
                # the connection is not auto committed by default, so we must commit to save our changes
                mydb.commit()
            st.success("#### Uploaded to database successfully!")
        
# MODIFY MENU    
if selected == "View & Modify":
    col1,col2,col3 = st.columns([3,3,2])
    st.subheader("**:violet[Change or Delete Existing data here]**")
    column1,column2 = st.columns(2,gap="large")
    try:
        with column1:
            mycursor.execute("SELECT Name FROM business_card")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
            st.markdown("#### Update or Modify any data below")
            mycursor.execute("select Company_Name,Name,Designation,Mobile_Number,Email,Website,Area,City,State,Pin_Code from business_card WHERE Name=%s",
                            (selected_card,))
            result = mycursor.fetchone()

            # DISPLAYING ALL THE INFORMATIONS
            company_name = st.text_input("Company_Name", result[0])
            card_holder = st.text_input("Name", result[1])
            designation = st.text_input("Designation", result[2])
            mobile_number = st.text_input("Mobile_Number", result[3])
            email = st.text_input("Email", result[4])
            website = st.text_input("Website", result[5])
            area = st.text_input("Area", result[6])
            city = st.text_input("City", result[7])
            state = st.text_input("State", result[8])
            pin_code = st.text_input("Pin_Code", result[9])

            if st.button("Update the Data"):
                # Update the information for the selected business card in the database
                mycursor.execute("""UPDATE business_card SET Company_Name=%s,Name=%s,Designation=%s,Mobile_Number=%s,Email=%s,Website=%s,Area=%s,City=%s,State=%s,Pin_Code=%s
                                    WHERE Name=%s""", (company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,selected_card))
                mydb.commit()
                st.success("Information updated in database successfully.")

        with column2:
            mycursor.execute("SELECT Name FROM business_card")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
            st.write(f"## You have selected :green[**{selected_card}'s**] card to delete")
            st.write("## Proceed to delete this card?")

            if st.button("Yes Delete Business Card"):
                mycursor.execute(f"DELETE FROM business_card WHERE Name='{selected_card}'")
                mydb.commit()
                st.success("Business card information deleted from database.")
    except:
        st.warning("There is no data available in the database")
    
    st.subheader(":violet[To View the Information stored in the Database]")
    if st.button("View Updated data"):
        mycursor.execute("select Company_Name,Name,Designation,Mobile_Number,Email,Website,Area,City,State,Pin_Code from business_card")
        updated_df = pd.DataFrame(mycursor.fetchall(),columns=["Company_Name","Name","Designation","Mobile_Number","Email","Website","Area","City","State","Pin_Code"])
        st.write(updated_df)
