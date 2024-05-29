
#include <core.p4>
#if __TARGET_TOFINO__ == 3
#include <t3na.p4>
#elif __TARGET_TOFINO__ == 2
#include <t2na.p4>
#else
#include <tna.p4>
#endif

#include "tofino_test_headers.p4"
#include "util.p4"



// ---------------------------------------------------------------------------
// Ingress parser
// ---------------------------------------------------------------------------

struct metadata_t {
    bit<16>     checksum;
}

parser SwitchIngressParser(
        packet_in pkt,
        out header_t hdr,
        out metadata_t ig_md,
        out ingress_intrinsic_metadata_t ig_intr_md) {

    TofinoIngressParser() tofino_parser;
    Checksum() tcp_csum;

    state start {
        tofino_parser.apply(pkt, ig_intr_md);
        transition parse_ethernet;
    }


    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition parse_ipv6;
    }

    state parse_ipv6 {
        pkt.extract(hdr.ipv6);
        tcp_csum.subtract({hdr.ipv6.src_addr,hdr.ipv6.dst_addr});
        transition select(hdr.ipv6.next_hdr){
		IP_PROTOCOLS_TCP:	parse_tcp;
		default:	accept;
	}
    }

    state parse_tcp {
        pkt.extract(hdr.tcp);
        tcp_csum.subtract({hdr.tcp.checksum});
        tcp_csum.subtract_all_and_deposit(ig_md.checksum);
        transition accept;
    }

}

// ---------------------------------------------------------------------------
// Ingress 
// ---------------------------------------------------------------------------

control SwitchIngress(
        inout header_t hdr,
        inout metadata_t ig_md,
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_prsr_md,
        inout ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t ig_tm_md) 
{
    action drop() {
        ig_dprsr_md.drop_ctl = 1;
    }

    action noAct() {

    }

    action route(macAddr_t dstAddr, PortId_t dst_port) {
        ig_tm_md.ucast_egress_port = dst_port;
        hdr.ethernet.dst_addr = dstAddr;
        hdr.ethernet.src_addr = hdr.ethernet.dst_addr;
        ig_dprsr_md.drop_ctl = 0;
    }

    action ipv6_p4nat_forward_c2s(macAddr_t dstAddr, PortId_t dst_port, ipv6_addr_t Addr) {
        ig_tm_md.ucast_egress_port = dst_port;
        hdr.ethernet.dst_addr = dstAddr;
        hdr.ethernet.src_addr = hdr.ethernet.dst_addr;
        hdr.ipv6.dst_addr = Addr;
        ig_dprsr_md.drop_ctl = 0;
    }

    action ipv6_p4nat_forward_s2c(macAddr_t dstAddr, PortId_t dst_port, ipv6_addr_t Addr) {
        ig_tm_md.ucast_egress_port = dst_port;
        hdr.ethernet.dst_addr = dstAddr;
        hdr.ethernet.src_addr = hdr.ethernet.dst_addr;
        hdr.ipv6.src_addr = Addr;
        ig_dprsr_md.drop_ctl = 0;
    }

    table ipv6_c2s {
        key = {
            hdr.ipv6.dst_addr: lpm;
        }
        actions = {
            ipv6_p4nat_forward_c2s;
            NoAction;
        }
        size = 1024;
        default_action = NoAction;
    }

    table ipv6_s2c {
        key = {
            hdr.ipv6.src_addr: lpm;
        }
        actions = {
            ipv6_p4nat_forward_s2c;
            NoAction;
        }
        size = 1024;
        default_action = NoAction;
    }
    apply {
        ig_tm_md.bypass_egress = 1;
        if(ig_intr_md.ingress_port == 65){	//c2s suid2000::4
		ig_tm_md.ucast_egress_port = 64;
		hdr.ethernet.src_addr = hdr.ethernet.dst_addr;
		hdr.ethernet.dst_addr = 161333219629;   
		ig_dprsr_md.drop_ctl = 0;}
	if(ig_intr_md.ingress_port == 64){	//s2c suid2000::4
		ig_tm_md.ucast_egress_port = 65;
		hdr.ethernet.src_addr = hdr.ethernet.dst_addr;
		hdr.ethernet.dst_addr = 95328068814;   
		ig_dprsr_md.drop_ctl = 0;}      
    }
}


// ---------------------------------------------------------------------------
// Ingress Deparser
// ---------------------------------------------------------------------------
control SwitchIngressDeparser(
        packet_out pkt,
        inout header_t hdr,
        in metadata_t ig_md,
        in ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md) 
{
    Checksum() tcp_csum;
    apply {
	if(hdr.tcp.isValid()){
        	hdr.tcp.checksum = tcp_csum.update({
            	hdr.ipv6.src_addr,
            	hdr.ipv6.dst_addr,
            	ig_md.checksum
        	});
	}
        pkt.emit(hdr.ethernet);
        pkt.emit(hdr.ipv6);
       // pkt.emit(hdr.tcp);
    }
}
// ---------------------------------------------------------------------------
// Egress parser
// ---------------------------------------------------------------------------
parser SwitchEgressParser(
        packet_in pkt,
        out header_t hdr,
        out metadata_t eg_md,
        out egress_intrinsic_metadata_t eg_intr_md) {
    TofinoEgressParser() tofino_parser;

    state start {
        pkt.extract(eg_intr_md);
        transition accept;
    }

}

// ---------------------------------------------------------------------------
// Egress Deparser
// ---------------------------------------------------------------------------
control SwitchEgressDeparser(
        packet_out pkt,
        inout header_t hdr,
        in metadata_t eg_md,
        in egress_intrinsic_metadata_for_deparser_t eg_dprsr_md) {


    apply {
        pkt.emit(hdr.ethernet);
	pkt.emit(hdr.ipv6);
	

    }
}


control SwitchEgress(
        inout header_t hdr,
        inout metadata_t eg_md,
        in egress_intrinsic_metadata_t eg_intr_md,
        in egress_intrinsic_metadata_from_parser_t eg_prsr_md,
        inout egress_intrinsic_metadata_for_deparser_t eg_dprsr_md,
        inout egress_intrinsic_metadata_for_output_port_t eg_tm_md) {



    apply {

    }
}

Pipeline(SwitchIngressParser(),
         SwitchIngress(),
         SwitchIngressDeparser(),
         SwitchEgressParser(),
         SwitchEgress(),
         SwitchEgressDeparser()) pipe;

Switch(pipe) main;
