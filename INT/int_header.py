from scapy.all import *

class int_header(Packet):
    fields_desc = [
        BitField("int_version", 0, 4),
        BitField("D", 0, 1),
        BitField("E", 0, 1),
        BitField("M", 0, 1),
        BitField("int_Reserved", 0, 12),
        BitField("Hop_ML", 0, 5),
        BitField("RemainingHopCount", 0, 8),
        BitField("Instruction_Bitmap", 0, 16),
        BitField("Domain_Specific_ID", 0, 16),
        BitField("DS_Instruction", 0, 16),
        BitField("DS_Flags", 0, 16),

    ]

class int_shim_header(Packet):
    fields_desc =[
        BitField("Type", 0, 4),
        BitField("NPT", 0, 2),
        BitField("R", 0, 2),
        BitField("Length", 0, 8),
        BitField("Reserved", 0, 8),
        BitField("IP_proto", 0, 8)
    ]

class int_metadata(Packet):
    fields_desc =[
        IntField("switchID", 0),
        IntField("hop_delay", 0),
        BitField("queue_depth", 0, 16),
        BitField("queue_delay", 0, 24),
        # BitField("link_delay", 0, 48),
        BitField("i_timestamp", 0, 48),
        BitField("e_timestamp", 0, 48)

    ]





bind_layers(TCP, int_shim_header)
bind_layers(int_shim_header, int_header),
bind_layers(int_header, int_metadata,int_version=2)




