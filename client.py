import socket
import xml.etree.ElementTree as ET

def send_query(query_file):
    with open(query_file, 'r') as file:
        query_str = file.read()
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 9999))
    
    client.send(query_str.encode())
    
    response = client.recv(4096).decode()
    client.close()
    
    root = ET.fromstring(response)
    print(f"Response from server for {query_file}:")
    for row in root.find('data').findall('row'):
        print({child.tag: child.text for child in row})


query_files = ["query1.xml", "query2.xml", "query3.xml", "query4.xml", "query5.xml"]
    
for query_file in query_files:
    print(f"Sending query from {query_file}")
    send_query(query_file)
    print("\n")