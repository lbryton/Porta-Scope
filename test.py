with open("./test/test.txt", 'r') as file:
    in_payload = False
    detect_time = 0
    payload_data = ""
    janout = file.read().split("\n")

    # Iterates through data
    for line in janout:
        # print(line)
        payload_cnt = 0
        if line.startswith('-> Triggering detection'):
            detect_time = line.split(" ")[3][1:-1]
            if in_payload:
                print(f"{str(detect_time)},{payload_data}\n")
                payload_data = ""
                payload_cnt += 1
            in_payload = True
        elif line.startswith('-> Invalid Packet CRC') and in_payload:
            in_payload = False
            payload_cnt +=1
            print(f"Invalid Packet CRC\n")

        elif in_payload and line.find("Application Data") != -1:
            packet_data = line.split(":")[2][1:]
            payload_data += packet_data

    if in_payload:
        if payload_data != "":
            print(f"{str(detect_time)},{payload_data}\n")
        else:
            print(f"No data\n")