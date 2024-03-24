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
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
