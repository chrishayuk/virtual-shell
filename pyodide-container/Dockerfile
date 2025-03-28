FROM node:18-slim

WORKDIR /app

# Install necessary packages and pyodide
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    npm install pyodide readline

# Copy the virtual shell code
COPY ./chuk_virtual_shell /app/chuk_virtual_shell/

# Copy the node runner script
COPY ./node_pyodide_shell.js /app/

# Make a directory for data persistence (optional)
RUN mkdir -p /app/data

# Environment variables
ENV NODE_ENV=production
ENV PYTHONUNBUFFERED=1

# Command to run the shell
CMD ["node", "node_pyodide_shell.js"]