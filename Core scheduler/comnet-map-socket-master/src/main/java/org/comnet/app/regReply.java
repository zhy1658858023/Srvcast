package org.comnet.app;

import org.onlab.packet.IPacket;

import java.nio.ByteBuffer;

public class regReply implements IPacket {
    private short num; //16位
    private short checksum; //16
    private byte type; //8
    private int reserve; //32
    private byte[] AID; //128
    private int RID; //32
    private short reserved; //16

    @Override
    public byte[] serialize() {
        byte[] data = new byte[30];
        ByteBuffer bb = ByteBuffer.wrap(data);
        bb.putShort(num);
        bb.putShort(checksum);
        bb.putInt(((this.type & 15) << 4 | this.reserve & 268435455));
        bb.put(this.AID);
        bb.putInt(RID);
        bb.putShort(reserved);
        return data;
    }

    /**
     * 注释：short到字节数组的转换！
     *
     * @param number
     * @return b
     */
    public static byte[] shortToByte(short number){
        int temp = number;
        byte[] b =new byte[2];
        for(int i =0; i < b.length; i++){
            b[i]=new Integer(temp &0xff).byteValue();//将最低位保存在最低位
            temp = temp >>8;// 向右移8位
        }
        return b;
    }

    /**
     * 注释：int到字节数组的转换！
     *
     * @param number
     * @return
     */
    public static byte[] intToByte(int number){
        int temp = number;
        byte[] b =new byte[4];
        for(int i =0; i < b.length; i++){
            b[i]=new Integer(temp &0xff).byteValue();//将最低位保存在最低位
            temp = temp >>8;// 向右移8位
        }
        return b;
    }

    public regReply(short num, short checksum, byte type, int reserve, byte[] AID, int RID, short reserved) {
        this.num = num;
        this.checksum = checksum;
        this.type = type;
        this.reserve = reserve;
        this.AID = AID;
        this.RID = RID;
        this.reserved = reserved;
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

    public byte[] getAID() {
        return AID;
    }

    public void setAID(byte[] AID) {
        this.AID = AID;
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
