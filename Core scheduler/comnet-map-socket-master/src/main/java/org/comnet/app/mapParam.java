package org.comnet.app;

import java.io.Serializable;

public class mapParam implements Serializable {
    private static final long serialVersionUID = -5535620314277211359L;;
    private byte nxt_hdr;
    private byte[] AID;
    private byte[] AIDdst;
    private String switchId;
    private String port;
    private byte[] MacAdress;

    public mapParam(byte nxt_hdr, byte[] AID, byte[] AIDdst, String switchId, String port, byte[] macAdress) {
        this.nxt_hdr = nxt_hdr;
        this.AID = AID;
        this.AIDdst = AIDdst;
        this.switchId = switchId;
        this.port = port;
        MacAdress = macAdress;
    }

    public byte getNxt_hdr() {
        return nxt_hdr;
    }

    public void setNxt_hdr(byte nxt_hdr) {
        this.nxt_hdr = nxt_hdr;
    }

    public byte[] getAID() {
        return AID;
    }

    public void setAID(byte[] AID) {
        this.AID = AID;
    }

    public byte[] getAIDdst() {
        return AIDdst;
    }

    public void setAIDdst(byte[] AIDdst) {
        this.AIDdst = AIDdst;
    }

    public String getSwitchId() {
        return switchId;
    }

    public void setSwitchId(String switchId) {
        this.switchId = switchId;
    }

    public String getPort() {
        return port;
    }

    public void setPort(String port) {
        this.port = port;
    }

    public byte[] getMacAdress() {
        return MacAdress;
    }

    public void setMacAdress(byte[] macAdress) {
        MacAdress = macAdress;
    }
}
