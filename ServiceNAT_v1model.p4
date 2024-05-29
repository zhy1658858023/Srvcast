/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<3>  res;
    bit<3>  ecn;
    bit<6>  ctrl;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

struct metadata {
    bit<16> tcpLength;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    tcp_t        tcp;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition parse_tcp;
    }

    state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }
    
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
        
    }

    action ipv4_p4nat_forward_c2s(macAddr_t dstAddr, egressSpec_t port, ip4Addr_t Addr) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.dstAddr = Addr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
        meta.tcpLength = hdr.ipv4.totalLen - (bit<16>)(hdr.ipv4.ihl)*4;
    }

    action ipv4_p4nat_forward_s2c(macAddr_t dstAddr, egressSpec_t port, ip4Addr_t Addr) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.srcAddr = Addr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
        meta.tcpLength = hdr.ipv4.totalLen - (bit<16>)(hdr.ipv4.ihl)*4;
    }
    
    table ipv4_c2s {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_p4nat_forward_c2s;
            NoAction;
        }
        size = 1024;
        default_action = NoAction;
    }

    table ipv4_s2c {
        key = {
            hdr.ipv4.srcAddr: lpm;
        }
        actions = {
            ipv4_p4nat_forward_s2c;
    
            NoAction;
        }
        size = 1024;
        default_action = NoAction;
    }
    
    apply {
         ipv4_c2s.apply();
	 ipv4_s2c.apply();
//	if (hdr.ipv4.dstAddr == 2886886402) {     //C to S,trans to port 1
  
//            standard_metadata.egress_spec = 1;
//	    hdr.ethernet.srcAddr = 161341233306;
//            hdr.ethernet.dstAddr = 272744414894187;
//            hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
//	    meta.tcpLength = hdr.ipv4.totalLen - (bit<16>)(hdr.ipv4.ihl)*4;
//        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	      hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);

    update_checksum_with_payload(
hdr.tcp.isValid(),
{ hdr.ipv4.srcAddr,
hdr.ipv4.dstAddr,
8w0,
hdr.ipv4.protocol,
meta.tcpLength,
hdr.tcp.srcPort,
hdr.tcp.dstPort,
hdr.tcp.seqNo,
hdr.tcp.ackNo,
hdr.tcp.dataOffset,
hdr.tcp.res,
hdr.tcp.ecn,
hdr.tcp.ctrl,
hdr.tcp.window,
16w0,
hdr.tcp.urgentPtr
},
hdr.tcp.checksum,
HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.tcp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
