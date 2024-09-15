/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#define MAX_HOPS 7

const bit<16> TYPE_IPV4 = 0x800;
const bit<16> TYPE_INT_HEADER = 0x1212;
const bit<16> TYPE_IPV6 = 0x86dd;


/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/
typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<128> ip6Addr_t;
typedef bit<32> switchID_t;
typedef bit<16> qDepth_t;
typedef bit<24> qDelay_t;
typedef bit<32> hopdelay_t;
typedef bit<48> linkdelay_t;



header ethernet_t {
	macAddr_t dstAddr;
	macAddr_t srcAddr;
	bit<16>   etherType;
}

header int_header_t {
	bit<4>      int_version;
    bit<1>      D;
    bit<1>      E;
    bit<1>      M;
    bit<12>     int_Reserved;   
    bit<5>      Hop_ML;
    bit<8>      RemainingHopCount;
    bit<16>     Instruction_Bitmap;
    bit<16>     Domain_Specific_ID;
    bit<16>     DS_Instruction;
    bit<16>     DS_Flags;
}

header int_metadata_t{
	switchID_t  switchID;
	hopdelay_t  hop_delay;
	qDepth_t    qDepth;
	qDelay_t    qDelay;
	// linkdelay_t link_delay;
	bit<48> i_timestamp;
	bit<48> e_timestamp;

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

header ipv6_t {
     bit<4> version;
     bit<8> trafficClass;
     bit<20> flowLabel;
     bit<16> payLoadLen;
     bit<8> nextHdr;
     bit<8> hopLimit;
     bit<128> srcAddr;
     bit<128> dstAddr;
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

header udp_t{
	bit<16> srcPort;
    bit<16> dstPort;
	bit<16> totalLen;
	bit<16> checksum;
}

header int_shim_t{
	bit<4>  Type;
	bit<2>  NPT;
	bit<2>  R;
	bit<8>  Length;
	bit<8>  Reserved;
	bit<8>  IP_proto;
}
struct metadata {
	bit<8>      temp_HopCount;

}

struct headers {
	ethernet_t		ethernet;
	int_header_t	int_header;
	int_metadata_t[MAX_HOPS]  int_metadata;
	ipv4_t          ipv4;
	ipv6_t          ipv6;
	tcp_t           tcp;
	udp_t           udp;
	int_shim_t      int_shim; 

	
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
            TYPE_IPV6: parse_ipv6;
			default: accept;
		}
	}

	state parse_ipv6 {
        packet.extract(hdr.ipv6);
        transition select(hdr.ipv6.nextHdr) {
            6: parse_tcp;
			17: parse_udp;
            default: accept;
        }
    }

	state parse_udp{
	 	packet.extract(hdr.udp);
		transition select(hdr.udp.dstPort){
			TYPE_INT_HEADER: parse_int_shim;
            default: accept;
		}
	}

	state parse_tcp {
        packet.extract(hdr.tcp);
		transition parse_int_shim;
       
    }

	state parse_int_shim{
	 	packet.extract(hdr.int_shim);
		packet.extract(hdr.int_header);
		transition  parse_hint;
	}
	

	state parse_hint {
		packet.extract(hdr.int_metadata.next);
	}

	state parse_ipv4 {
            packet.extract(hdr.ipv4);
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

    action ipv6_forward(macAddr_t dstAddr, egressSpec_t port) {
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv6.hopLimit=hdr.ipv6.hopLimit-1;
        standard_metadata.egress_spec = port;
    }
    
    table ipv6_lpm{
    	key = {
            hdr.ipv6.dstAddr: exact;
        }
        actions = {
            ipv6_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

	apply {
		
		if (hdr.ipv6.isValid()) {
			ipv6_lpm.apply();
                        
		}
	}
}


/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
				inout metadata meta,
				inout standard_metadata_t standard_metadata) {

	action add_swtrace(switchID_t swid){
		hdr.int_shim.setValid();
		hdr.int_shim.Type = 1;
		hdr.int_shim.NPT = 0;
		hdr.int_shim.Length = 7;
		hdr.int_shim.IP_proto = 0;

		hdr.int_header.setValid();
		hdr.int_header.int_version=2;
		hdr.int_header.Hop_ML=2;
		hdr.int_header.RemainingHopCount=MAX_HOPS;
		hdr.int_header.Instruction_Bitmap = 40960;

		hdr.int_metadata.push_front(1);
		hdr.int_metadata[0].setValid();
		hdr.int_metadata[0].switchID = swid;
		hdr.int_metadata[0].qDepth = (bit <16>) standard_metadata.enq_qdepth;
		hdr.int_metadata[0].qDelay = (bit <24>)standard_metadata.deq_timedelta;
		hdr.int_metadata[0].hop_delay = (bit <32>) standard_metadata.egress_global_timestamp - (bit <32>) standard_metadata.ingress_global_timestamp + (bit <32>) standard_metadata.deq_timedelta;  //Hop delay is in us
		// hdr.int_metadata[0].link_delay = 0;
		hdr.int_metadata[0].i_timestamp = standard_metadata.ingress_global_timestamp;
		hdr.int_metadata[0].e_timestamp = standard_metadata.egress_global_timestamp;

	}

	action transition_swtrace(switchID_t swid){
		meta.temp_HopCount = hdr.int_header.RemainingHopCount;
		hdr.int_header.RemainingHopCount= meta.temp_HopCount-1;
		hdr.int_metadata.push_front(1);
		hdr.int_metadata[0].setValid();
		hdr.int_metadata[0].switchID = swid;
		hdr.int_metadata[0].qDepth = (bit <16>) standard_metadata.enq_qdepth;//Queue depth is in pkts
		hdr.int_metadata[0].qDelay = (bit <24>)standard_metadata.deq_timedelta; //Queue delay is in us
		hdr.int_metadata[0].hop_delay = (bit <32>) standard_metadata.egress_global_timestamp - (bit <32>) standard_metadata.ingress_global_timestamp + (bit <32>) standard_metadata.deq_timedelta;  //Hop delay is in us
		// hdr.int_metadata[0].link_delay = standard_metadata.ingress_global_timestamp -hdr.int_metadata[1].e_timestamp;
		hdr.int_metadata[0].i_timestamp = standard_metadata.ingress_global_timestamp;
		hdr.int_metadata[0].e_timestamp = standard_metadata.egress_global_timestamp;
	}
	
	table swtrace {
		actions = {
			add_swtrace;
			transition_swtrace;
  			NoAction;
		}
		default_action = NoAction();
	}



	apply {
            swtrace.apply();    
               
                
	}
}


/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
	apply {
		update_checksum(
			hdr.ipv4.isValid(), {
			hdr.ipv4.version,
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
	}
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
	apply {
		packet.emit(hdr.ethernet);
		packet.emit(hdr.ipv6);
		packet.emit(hdr.tcp);
		packet.emit(hdr.int_shim);
		packet.emit(hdr.int_header);
		packet.emit(hdr.int_metadata);
		
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