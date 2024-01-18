# Use an Python runtime as an image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Install And Copy any needed packages specified in requirements.txt
COPY weatherApp/ /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn
RUN pip install gunicorn

# Expose port 5000
EXPOSE 5000

# Run your gunicorn when the container launches
CMD ["gunicorn", "-b", "0.0.0.0:5000", "FinalProject:app"]