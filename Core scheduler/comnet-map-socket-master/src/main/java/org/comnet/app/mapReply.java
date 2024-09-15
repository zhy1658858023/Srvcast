package org.comnet.app;

import org.onlab.packet.IPacket;

import java.nio.ByteBuffer;

public class mapReply implements IPacket {
    private short num; //16wei
    private short checksum; //16
    private byte type; //8 4
    private byte R; //8 4
    private byte error; //8 4
    private int reserve; //32 20
    private byte[] AID; //32
    private int RID; //16
    private short reserved; //16

    @Override
    public byte[] serialize() {
        byte[] data = new byte[30];
        ByteBuffer bb = ByteBuffer.wrap(data);
        bb.putShort(num);
        bb.putShort(checksum);
        bb.putInt(((this.type & 15) << 28 | (this.R & 15) << 24 | (this.error & 15) << 20 | this.reserve & 1048575));
        bb.put(this.AID);
        bb.putInt(RID);
        bb.putShort(reserved);
        return data;
    }


    public byte getR() {
        return R;
    }

    public void setR(byte r) {
        R = r;
    }

    public byte getError() {
        return error;
    }

    public void setError(byte error) {
        this.error = error;
    }

    public int getRID() {
        return RID;
    }

    public void setRID(int RID) {
        this.RID = RID;
    }

    public short getReserved() {
        return reserved;
    }

    public void setReserved(short reserved) {
        this.reserved = reserved;
    }

    public short getNum() {
        return num;
    }

    public void setNum(short num) {
        this.num = num;
    }

    public short getChecksum() {
        return checksum;
    }

    public void setChecksum(short checksum) {
        this.checksum = checksum;
    }

    public byte getType() {
        return type;
    }

    public void setType(byte type) {
        this.type = type;
    }

    public int getReserve() {
        return reserve;
    }

    public void setReserve(int reserve) {
        this.reserve = reserve;
    }

    public byte[] getAID() {
        return AID;
    }

    public void setAID(byte[] AID) {
        this.AID = AID;
    }

    public mapReply(short num, short checksum, byte type, byte r, byte error, int reserve, byte[] AID, int RID, short reserved) {
        this.num = num;
        this.checksum = checksum;
        this.type = type;
        R = r;
        this.error = error;
        this.reserve = reserve;
        this.AID = AID;
        this.RID = RID;
        this.reserved = reserved;
    }

    @Override
    public IPacket getPayload() {
        return null;
    }

    @Override
    public IPacket setPayload(IPacket packet) {
        return null;
    }

    @Override
    public IPacket getParent() {
        return null;
    }

    @Override
    public IPacket setParent(IPacket packet) {
        return null;
    }

    @Override
    public void resetChecksum() {

    }


}
