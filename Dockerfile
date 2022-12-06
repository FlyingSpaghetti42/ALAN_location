FROM python:3.10.6-buster

WORKDIR /ALAN_location

# copy everything from cur dir (local) to cur dir (image)
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD streamlit run interface.py

#taxifare.api.fast:app --port $PORT 0.0.0.0
