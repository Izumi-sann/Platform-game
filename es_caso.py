ip1 = "10.0.0.255"
ip2 = "10.0.1.0"

        
def ip_counter_2(ip1, ip2):
    ip1 = [int(x) for x in ip1.split('.')]
    ip2 = [int(x) for x in ip2.split('.')]
    
    index = [256**x for x in range(3, -1, -1)]            
    
    for i, value in enumerate(ip1):
        ip1[i] = value * index[i]
    for i, value in enumerate(ip2):
        ip2[i] = value * index[i]
        
    ip2 = sum(ip2)
    ip1 = sum(ip1)
    
    difference = -1 * (ip1 - ip2)
    return difference
        
def numeric_address(text):
    
    return int.from_bytes(
        bytes(map(int, text.split(".")))
    )

def ip_range(start, end):
    return numeric_address(end) - numeric_address(start)

print(ip_counter_2(ip1, ip2))
#print(ip_range(ip1, ip2))