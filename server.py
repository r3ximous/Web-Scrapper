import socket
import csv
import xml.etree.ElementTree as ET
import os
from datetime import datetime

# Path to the CSV file
csv_file = "directory.csv"

def load_employees():
    employees = []
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            employees.append(row)
    return employees

def filter_employees(conditions, employees):
    filtered = employees
    for key, value in conditions.items():
        filtered = [emp for emp in filtered if emp.get(key) == value]
    return filtered

def handle_client(client_socket, employees):
    request = client_socket.recv(4096).decode()
    root = ET.fromstring(request)
    
    conditions = {child.find('column').text.strip(): child.find('value').text.strip() for child in root.findall('condition')}
    filtered_employees = filter_employees(conditions, employees)
    
    response = ET.Element("result")
    status = ET.SubElement(response, "status")
    status.text = "success"
    data = ET.SubElement(response, "data")
    
    for emp in filtered_employees:
        row = ET.SubElement(data, "row")
        for key, value in emp.items():
            child = ET.SubElement(row, key)
            child.text = value
    
    response_str = ET.tostring(response).decode()
    client_socket.send(response_str.encode())
    
    # Save the response to an XML file
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    response_filename = f"response_{timestamp}.xml"
    with open(response_filename, 'w') as file:
        file.write(response_str)
    
    client_socket.close()


employees = load_employees()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 9999))
server.listen(5)
print("Server listening on port 9999")
    
while True:
    client_socket, addr = server.accept()
    handle_client(client_socket, employees)
