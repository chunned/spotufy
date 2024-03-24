FROM python:3.10-slim

# Install Gunicorn
RUN pip3 install gunicorn

# Copy the application files
COPY . /spotufy
WORKDIR /spotufy

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Expose port 8080 for Gunicorn
EXPOSE 8080

# Start Gunicorn
<<<<<<< HEAD
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
=======
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
>>>>>>> 3f9f8e7eaf076fd30e5cd06291e5ec6634cc3ba3
