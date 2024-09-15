/*
 * Copyright 2021-present Open Networking Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.comnet.app;

import org.onlab.packet.*;
import org.onlab.util.SharedScheduledExecutors;
import org.onosproject.cfg.ComponentConfigService;
import org.onosproject.core.ApplicationId;
import org.onosproject.core.CoreService;
import org.onosproject.net.DeviceId;
import org.onosproject.net.Path;
import org.onosproject.net.PortNumber;
import org.onosproject.net.flow.*;
import org.onosproject.net.flow.criteria.PiCriterion;
import org.onosproject.net.packet.*;
import org.onosproject.net.pi.model.PiActionId;
import org.onosproject.net.pi.model.PiActionParamId;
import org.onosproject.net.pi.model.PiMatchFieldId;
import org.onosproject.net.pi.model.PiTableId;
import org.onosproject.net.pi.runtime.PiAction;
import org.onosproject.net.pi.runtime.PiActionParam;
import org.onosproject.store.service.StorageService;
import org.osgi.service.component.ComponentContext;
import org.osgi.service.component.annotations.Activate;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Deactivate;
import org.osgi.service.component.annotations.Modified;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.swing.event.TreeSelectionEvent;
import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputStream;
import java.math.BigInteger;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.sql.*;
import java.util.*;
import java.util.concurrent.TimeUnit;

import static org.onlab.util.Tools.get;
import static org.onosproject.net.DeviceId.deviceId;
import static org.onosproject.net.PortNumber.fromString;
import static org.onosproject.net.PortNumber.portNumber;
/////////////////////////////////////////////////////////////////////////////////////////////
import org.onosproject.net.topology.Topology;
import org.onosproject.net.topology.TopologyService;
import com.google.common.collect.Lists;
import org.onosproject.net.Link;
/////////////////////////////////////////////////////////////////////////////////////////////
/**
 * Skeletal ONOS application component.
 */
@Component(immediate = true,
           service = {comnetmapAPP.class},
           property = {
               "someProperty=Some Default String Value",
           })
public class comnetmapAPP {

    private final Logger log = LoggerFactory.getLogger(getClass());

    /** Some configurable property. */
    private String someProperty;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected ComponentConfigService cfgService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected StorageService storageService;


    private static final String APP_NAME = "comnetmapAPP";

    // Default priority used for flow rules installed by this app.
    private static final int FLOW_RULE_PRIORITY = 100;
    //    private final HostListener hostListener = new InternalHostListener();
    private ApplicationId appId;
////////////////////////////////////////////////////////////////////////////////////////////////
    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private TopologyService topologyService;
////////////////////////////////////////////////////////////////////////////////////////////////
    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private CoreService coreService;
    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    private FlowRuleService flowRuleService;
    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected PacketService packetService;
    private boolean listen = false;

    @Activate
    protected void activate() {
        cfgService.registerProperties(getClass());
        appId = coreService.registerApplication(APP_NAME);
        listen=true;
        scheduleTask(new Runnable() {
            @Override
            public void run() {
                socketSer();
            }
        },0);

        printlog();
        log.info("comnetmapAPP Startd");
    }

    @Deactivate
    protected void deactivate() {
        cfgService.unregisterProperties(getClass(), false);
        flowRuleService.removeFlowRulesById(appId);
        listen=false;
        log.info("comnetmapAPP Stopped");
    }

    @Modified
    public void modified(ComponentContext context) {
        Dictionary<?, ?> properties = context != null ? context.getProperties() : new Properties();
        if (context != null) {
            someProperty = get(properties, "someProperty");
        }
        log.info("Reconfigured");
    }

    /**
     * Schedules a task for the future using the executor service managed by
     * this component.
     *
     * @param task         task runnable
     * @param delaySeconds delay in seconds
     */
    public void scheduleTask(Runnable task, int delaySeconds) {
        SharedScheduledExecutors.newTimeout(
                task,
                delaySeconds, TimeUnit.SECONDS);
    }

    private void socketSer(){
        /**
         * 根据tcp协议可知，所谓套接字（socket）是指一个由“ip地址+端口”组成的组合。
         * 而每一台主机的ip地址都是确定的，不需要我们来指定，
         * 所以构建服务器socket的第一步就是确定端口
         */
        try {
            int port = 60002;//端口号
            //int queueLength = 50;//最大入站连接
            InetAddress bindAddress = InetAddress.getByName("127.0.0.1");//只监听该ip的指定端口
            //ExecutorService pool = Executors.newFixedThreadPool(50);//创建一个最大容量为50的线程池，为每一个入站连接分配一条线程。

            //创建一个端口为“60002”的服务器socket
            ServerSocket serverSocket = new ServerSocket(port);

            while (listen){
                //accept()调用会阻塞，会一直等到有客户端连接到指定socket端口为止。
                final Socket connection = serverSocket.accept();
                //线程池中拿取一条线程来处理socket连接。然后主程序运行下一个循环，继续等待下一个客户端的访问。
                scheduleTask(new Runnable() {
                    public void run() {
                        try {
                            log.info("socketSer进入线程");
                            InputStream inputStream = connection.getInputStream();
                            ObjectInputStream is = new ObjectInputStream(inputStream);
                            Object obj = null;
                            while((obj = is.readObject())!=null){
                                log.info("**************** 收到APP转发的内容 ****************");
                                mapParam mapparam = (mapParam) obj;
                                log.info("********* nxt_hdr= " + mapparam.getNxt_hdr());
                                byte nxt_hdr = mapparam.getNxt_hdr();
                                log.info("********* AIDsrc= " + new BigInteger(mapparam.getAID()));
                                byte[] AIDsrc = mapparam.getAID();
                                log.info("********* AIDdst= " + new BigInteger(mapparam.getAIDdst()));
                                byte[] AIDdst = mapparam.getAIDdst();
                                log.info("********* DeviceId= " + mapparam.getSwitchId().toString());
                                String switchId = mapparam.getSwitchId();
                                DeviceId switchIdN = deviceId(switchId);
                                log.info("********* Port= " + mapparam.getPort().toString());
                                String port = mapparam.getPort();
                                PortNumber portN = fromString(port);

                                byte[] MacAdress = mapparam.getMacAdress();
                                mapping(nxt_hdr,AIDsrc,AIDdst,switchIdN,portN,MacAdress);
                                is.close();
                            }
                        } catch (IOException | ClassNotFoundException e) {
                            e.printStackTrace();
                            log.info("************"+e.getMessage());
                        } finally {
                            try {
                                //关闭socket连接
                                connection.close();
                            } catch (IOException e) {
                                e.printStackTrace();
                                log.info("************"+e.getMessage());
                            }
                        }
                    }

                },0);

            }
        } catch (IOException e) {
            e.printStackTrace();
            log.info("************"+e.getMessage());
        }
    }


    public void mapping(byte next_hdr,byte[] AID,byte[] AIDdst,DeviceId switchId,PortNumber port,byte[] MacAdress) {
        log.info("********************************connecting MySQL**********************************" );
        Connection conn = null;
        PreparedStatement prestate = null;
        ResultSet rs = null;
        ResultSet rs_all;
        try {
            //1。注册驱动
            Driver driver = new com.mysql.cj.jdbc.Driver();
            DriverManager.registerDriver(driver);
            log.info("********************************注册MySQL驱动成功********************************");

            //2。获取连接
            conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/comnet?serverTimezone=UTC","root","bjtu903");

            log.info("********************************connected to database: "+ conn + "*******************************");

            //3。获取预编译的数据库操作对象(PreparedStatement是预编译的数据库操作对象)
            //判断操作类型
            switch (next_hdr){
                case (byte) 144: //注册操作
                    log.info("*************  为认证成功的终端"+ new BigInteger(AID) +"注册 **************");
                    //判断此AID是否已经注册
                    String pre_query = "select RID from mapping where AID =?";
                    prestate = conn.prepareStatement(pre_query);
                    prestate.setString(1,new BigInteger(AID).toString());
                    //执行sql
                    boolean flag = prestate.executeQuery().next();
                    if(!flag){ //当这个AID没有注册过
                        //获取随机数
                        int i = 0;
                        int[] result = randomCommon(100,200,50);
                        int RID_insert =  result[i];
                        //检查随机数是否重复
                        String queryall  = "select * from mapping";
                        prestate = conn.prepareStatement(queryall);
                        rs_all = prestate.executeQuery(queryall);
                        while(rs_all.next()){
                            int RIDx = rs_all.getInt("RID");
                            if(RIDx==RID_insert){
                                RID_insert= result[++i];
                            }
                        }
                        log.info("*************  已从RID池中选取RID"+RID_insert+"分配给用户 "+ new BigInteger(AID));

                        //注册动作
                        String insert = "insert into mapping(AID,RID,SWITHID) values(?,?,?)";
                        prestate = conn.prepareStatement(insert);
                        prestate.setString(1,new BigInteger(AID).toString());
                        prestate.setInt(2,RID_insert);
                        prestate.setString(3,switchId.toString());
                        //4。执行sql
                        log.info("*************  开始注册 **************");
                        int count_insert = prestate.executeUpdate();
                        log.info(count_insert == 1 ? "******** 注册成功！*************" : "********** 注册失败! ***********");
                        log.info("************* 注册条目为：AID= "+ new BigInteger(AID) +" | RID = "+RID_insert+"************");

                        log.info("*******************开始为此ASR分发change_src流表项***********************");
                        change_src(switchId,Ip6Address.valueOf(AID),RID_insert,(short) port.toLong());
                        log.info("************* 已下发注册内容流表： "+ new BigInteger(AID) + "--" + RID_insert);
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                        String search = "select SWITHID from mapping where SWITHID !=?";
                        prestate = conn.prepareStatement(search);
                        prestate.setString(1,switchId.toString());
                        List<String> switchlist = new ArrayList<>();
                        rs_all = prestate.executeQuery();
                        while(rs_all.next()){
                            String swithid = rs_all.getString("SWITHID");
                            switchlist.add(swithid);
                            log.info(swithid);
                        }
                        for (String swi : switchlist)
                        {
                            String searchrid = "select RID from mapping where SWITHID = ?";
                            prestate = conn.prepareStatement(searchrid);
                            prestate.setString(1,swi);
                            rs_all = prestate.executeQuery();
                            while(rs_all.next()){
                                int rid = rs_all.getInt("RID");
                                Topology topo;
                                topo = topologyService.currentTopology();
                                Set<Path> allPaths = topologyService.getPaths(topo, deviceId(swi), switchId);
                                if (allPaths.size() == 0) {
                                    log.info("----------------{}和{}之间没有链路------------------------", switchId, deviceId(swi));
                                    break;
                                }
                                List<Link> pathLinks = pickRandomPath(allPaths).links();
                                for (Link link : pathLinks) {
                                    DeviceId swsrc = link.src().deviceId();
                                    DeviceId swdst = link.dst().deviceId();
                                    PortNumber portnudst = link.dst().port();
                                    if(swdst.toString().equals(switchId.toString()))
                                    {
                                        insertRidForwardRule2(swdst, portnudst, rid);
                                    }
                                    else
                                    {
                                        insertRidForwardRule(swdst, portnudst, rid);
                                    }
                                    PortNumber portnusrc = link.src().port();
                                    if(swsrc.toString().equals(deviceId(swi).toString()))
                                    {
                                        insertRidForwardRule2(swsrc, portnusrc, RID_insert);
                                    }
                                    else
                                    {
                                        insertRidForwardRule(swsrc, portnusrc, RID_insert);
                                    }


                                }

                            }
                        }
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
                        replyRegPkt(switchId, port, AIDdst , MacAdress,AID,RID_insert);
                    }else{
                        log.info("终端"+new BigInteger(AID)+"已注册过");
                    }
                    break;
                case (byte) 146: //查询操作(封装时查询目的RID)
                    log.info("************************* 收到comnet查询报文 ********************************************");
                    String query = "select RID from mapping where AID =?";
                    prestate = conn.prepareStatement(query);
                    prestate.setString(1,new BigInteger(AIDdst).toString());
                    //执行sql
                    rs = prestate.executeQuery();
                    rs.next();
                    int RID_query = rs.getInt("RID");
                    log.info("*************** 查询条目为："+ new BigInteger(AIDdst) + "｜" + RID_query+" ****************");

                    //流表change_dst table
                    log.info("*******************开始为此ASR分发change_dst流表项***********************");
                    change_dst(switchId,Ip6Address.valueOf(AIDdst),RID_query);
                    log.info("*************** 已下发查询内容流表: "+ new BigInteger(AIDdst) + "--" + RID_query);

                    replyMapPkt(switchId, port, AIDdst, MacAdress,AID,RID_query);
                    break;
                case (byte) 154: //删除操作
                    String delete = "delete from mapping where AID =?";
                    prestate = conn.prepareStatement(delete);
                    prestate.setString(1,new BigInteger(AID).toString());
                    //执行sql
                    int count_delete = prestate.executeUpdate();
                    System.out.println(count_delete == 1 ? "delete succeed!" : "delete failed!");
                    break;
                case (byte) 155: //更新操作
                    //获取随机数
                    int result1[] = randomCommon(0,32767,100);
                    String check = "select RID from mapping where AID =?";
                    prestate = conn.prepareStatement(check);
                    prestate.setString(1,new BigInteger(AID).toString());
                    //执行sql
                    rs = prestate.executeQuery();
                    rs.next();
                    int oldRID = rs.getInt("RID");
                    log.info("old RID = "+oldRID);
                    for (int RID_update:result1) {
                        if(oldRID!=RID_update){
                            String update = "update mapping set RID = ? where AID = ?";
                            prestate = conn.prepareStatement(update);
                            prestate.setInt(1,RID_update);
                            prestate.setString(2,new BigInteger(AID).toString());
                            int count_update = prestate.executeUpdate();
                            System.out.println(count_update == 1 ? "update succeed!" : "update failed!");
                            System.out.println("RID_update = " + RID_update);
                            break;
                        }
                    }
                    break;
                case 0: //查询所有表项
                    String queryall  = "select * from mapping";
                    prestate = conn.prepareStatement(queryall);
                    rs_all = prestate.executeQuery(queryall);
                    //5。处理结果集
                    while(rs_all.next()){
                        int RIDx = rs_all.getInt("RID");
                        String AIDx = rs_all.getString("AID");
                        System.out.println("AID = " + AIDx + "  ｜ " + "RID = " + RIDx);
                    }
                    break;
            }
        } catch (SQLException e) {
            e.printStackTrace();
            log.info("******** SQLException:"+e.getMessage());
        } finally {
            //6。释放资源
            if(rs != null){
                try {
                    rs.close();
                } catch (SQLException e) {
                    e.printStackTrace();
                }
            }
            if(prestate != null){
                try {
                    prestate.close();
                } catch (SQLException e) {
                    e.printStackTrace();
                }
            }
            if(conn != null){
                try {
                    conn.close();
                } catch (SQLException e) {
                    e.printStackTrace();
                }
            }
        }
        log.info("************************与数据库交互结束**********************");

    }

    /**
     * 随机指定范围内N个不重复的数
     * 最简单最基本的方法
     * @param min 指定范围最小值
     * @param max 指定范围最大值
     * @param n 随机数个数
     */
    public int[] randomCommon(int min, int max, int n){
        if (n > (max - min + 1) || max < min) {
            return null;
        }
        int[] result = new int[n];
        int count = 0;
        while(count < n) {
            int num = (int) (Math.random() * (max - min)) + min;
            boolean flag = true;
            for (int j = 0; j < n; j++) {
                if(num == result[j]){
                    flag = false;
                    break;
                }
            }
            if(flag){
                result[count] = num;
                count++;
            }
        }
        return result;
    }


    public void change_dst(DeviceId switchId,Ip6Address aid,int riddst){
        //匹配的表
        PiTableId enable_rid = PiTableId.of("MyIngress.change_dst");
        //匹配的key
        final PiMatchFieldId uidDestMatchFieldId = PiMatchFieldId.of("hdr.aid.aid_d");
        final PiCriterion match = PiCriterion.builder()
                .matchExact(uidDestMatchFieldId,aid.toOctets())
                .build();

        //action的参数
//        final PiActionParamId rids = PiActionParamId.of("rids");
//        final PiActionParam ridsParam = new PiActionParam(rids, ridsrc);

        //action的参数
        final PiActionParamId ridd = PiActionParamId.of("RID_d");
        final PiActionParam riddParam = new PiActionParam(ridd, riddst);

        ArrayList<PiActionParam> params= new ArrayList<>();
        params.add(riddParam);

        //创建anction
        final PiActionId ingressActionId = PiActionId.of("MyIngress.encapsulate_dst");
        final PiAction action = PiAction.builder()
                .withId(ingressActionId)
                .withParameters(params)
                .build();

        //insertPiFlowRule(switchId, enable_rid, match, action);
        insertPiFlowRulemakeTemporary(switchId, enable_rid, match, action);
        log.info("*****TABLE change_dst Inserting rule on switch {}: table={}, match={}, action={}",
                switchId, enable_rid, match, action);
    }

    public void change_src(DeviceId switchId,Ip6Address aid,int riddst,short port){
        //匹配的表
        PiTableId change_src = PiTableId.of("MyIngress.change_src");
        //匹配的key
        final PiMatchFieldId uidDestMatchFieldId = PiMatchFieldId.of("hdr.aid.aid_s");
////////////////////////////////////////////////////////////////////////////////////////////////////////
        final PiMatchFieldId ingressport = PiMatchFieldId.of("meta.inport");
////////////////////////////////////////////////////////////////////////////////////////////////////////
        final PiCriterion match = PiCriterion.builder()
                .matchExact(uidDestMatchFieldId,aid.toOctets())
///////////////////////////////////////////////////////////////////////////////////////////////////////
                .matchExact(ingressport,port)
///////////////////////////////////////////////////////////////////////////////////////////////////////
                .build();

        //action的参数
        final PiActionParamId ridd = PiActionParamId.of("RID_s");
        final PiActionParam riddParam = new PiActionParam(ridd, riddst);

        ArrayList<PiActionParam> params= new ArrayList<>();
        params.add(riddParam);

        //创建action
        final PiActionId ingressActionId = PiActionId.of("MyIngress.encapsulate_src");
        final PiAction action = PiAction.builder()
                .withId(ingressActionId)
                .withParameters(params)
                .build();

        //insertPiFlowRule(switchId, change_src, match, action);
        insertPiFlowRulemakeTemporary(switchId, change_src, match, action);
        log.info("*****TABLE change_src Inserting rule on switch {}: table={}, match={}, action={}",
                switchId, change_src, match, action);
    }
////////////////////////////////////////////////////////////////////////////////////////////////
public void insertRidForwardRule2(DeviceId deviceId,PortNumber portNumber,int rid){
    PiTableId enable_rid = PiTableId.of("MyIngress.RID_forward_ASR");
    //匹配的key
    final PiMatchFieldId ridMatchFieldId_ASR = PiMatchFieldId.of("meta.myrid");
    final PiCriterion match = PiCriterion.builder()
            .matchExact(ridMatchFieldId_ASR,rid)
            .build();

    //action的参数
    final PiActionParamId port = PiActionParamId.of("port");
    final PiActionParam portParam = new PiActionParam(port, (short)portNumber.toLong());

    //创建anction
    final PiActionId ingressActionId = PiActionId.of("MyIngress.rid_forward");
    final PiAction action = PiAction.builder()
            .withId(ingressActionId)
            .withParameter(portParam)
            .build();

    //insertPiFlowRule(deviceId, enable_rid, match, action);
    insertPiFlowRulemakeTemporary(deviceId, enable_rid, match, action);
    log.info("*****TABLE change_dst Inserting rule on switch {}: table={}, match={}, action={}",
            deviceId, enable_rid, match, action);
}
////////////////////////////////////////////////////////////////////////////////////////////

    private void insertPiFlowRule(DeviceId switchId, PiTableId tableId,
                                  PiCriterion piCriterion, PiAction piAction) {
        FlowRule rule = DefaultFlowRule.builder()
                .forDevice(switchId)
                .forTable(tableId)
                .fromApp(appId)
                .withPriority(FLOW_RULE_PRIORITY)
                .makePermanent()
                .withSelector(DefaultTrafficSelector.builder()
                        .matchPi(piCriterion).build())
                .withTreatment(DefaultTrafficTreatment.builder()
                        .piTableAction(piAction).build())
                .build();
        flowRuleService.applyFlowRules(rule);
    }


    public void replyRegPkt(DeviceId deviceId, PortNumber portNumber, byte[] destipaddr, byte[] destmacaddr,byte[] AID,int RID){
        log.info("***************************开始回复映射发布报文************************");
        if (deviceId!=null && portNumber != null){
            IPv6 replyIpv6Pkt = new IPv6();
            replyIpv6Pkt.setDestinationAddress(destipaddr);
            byte flag = 0;
//            short fragmentoffset = 2;
            byte protocol = (byte) 145; //映射发布报文下一个首部值为3
            replyIpv6Pkt.setNextHeader(protocol);
            replyIpv6Pkt.setHopLimit((byte) 127);
            replyIpv6Pkt.setPayload(new regReply((short)1,(short)0,(byte)145,0,AID,RID,(short)0));
//            replyIpv4Pkt.setFragmentOffset(fragmentoffset);
            Ethernet replyEthPkt = new Ethernet();
            replyEthPkt.setDestinationMACAddress(destmacaddr).setSourceMACAddress(destmacaddr)
                    .setEtherType(Ethernet.TYPE_IPV6)
                    .setPayload(replyIpv6Pkt);

            byte[] finalPkt = replyEthPkt.serialize();

            DefaultOutboundPacket outPkt = new DefaultOutboundPacket(deviceId, DefaultTrafficTreatment.builder().setOutput(portNumber).build(), ByteBuffer.wrap(finalPkt));

            packetService.emit(outPkt);
            log.info("****************发送Reg-reply***************");
        }else {
            log.info("********************device/port获取失败****发送失败*****************");}
    }

    public void replyMapPkt(DeviceId deviceId, PortNumber portNumber, byte[] destipaddr, byte[] destmacaddr,byte[] AID,int RID){
        log.info("***************************开始回复映射查询报文************************");
        if (deviceId!=null && portNumber != null){
            log.info("******************** replyMapPkt-1 *********************");
            IPv6 replyIpv6Pkt = new IPv6();
            replyIpv6Pkt.setDestinationAddress(destipaddr);
            log.info("******************** replyMapPkt-2 *********************");
            byte flag = 0;
//            short fragmentoffset = 2;
            byte protocol = (byte) 146; //映射查询报文的下一个首部值为4
            replyIpv6Pkt.setNextHeader(protocol);
            replyIpv6Pkt.setHopLimit((byte)127);
            log.info("******************** replyMapPkt-3 *********************");
            replyIpv6Pkt.setPayload(new mapReply((short)1,(short)0,(byte)146,(byte)0,(byte)0,(byte)0,destipaddr,RID,(short)0));
            log.info("******************** replyMapPkt-4 *********************");
//            replyIpv4Pkt.setFragmentOffset(fragmentoffset);
            Ethernet replyEthPkt = new Ethernet();
            replyEthPkt.setDestinationMACAddress(destmacaddr).setSourceMACAddress(destmacaddr)
                    .setEtherType(Ethernet.TYPE_IPV6).setPayload(replyIpv6Pkt);
            log.info("******************** replyMapPkt-5 *********************");
            byte[] finalPkt = replyEthPkt.serialize();
            log.info("******************** replyMapPkt-6 *********************");
            DefaultOutboundPacket outPkt = new DefaultOutboundPacket(deviceId, DefaultTrafficTreatment.builder().setOutput(portNumber).build(), ByteBuffer.wrap(finalPkt));
            log.info("******************** replyMapPkt-7 *********************");
            packetService.emit(outPkt);
            log.info("****************发送reply***************");
        }else {
            log.info("********************device/port获取失败****发送失败*****************");}
    }




    private boolean iscomnetPacket(Ethernet eth) {
        return eth.getEtherType() == Ethernet.TYPE_IPV6;
    }


    private boolean isControlPacket(Ethernet eth) {
        short type = eth.getEtherType();
        return type == Ethernet.TYPE_LLDP || type == Ethernet.TYPE_BSN;
    }

    public void printlog(){

        for (int i = 0; i < 20; i++) {
            log.info("**********************************       "+i+"        **********************************");
        }
    }
///////////////////////////////////////////////////////////////////////////////////////////////////////
    private Path pickRandomPath(Set<Path> paths) {
        int item = new Random().nextInt(paths.size());
        List<Path> pathList = Lists.newArrayList(paths);
        return pathList.get(item);
    }

    public void insertRidForwardRule(DeviceId deviceId,PortNumber portNumber,int rid){
        PiTableId enable_rid = PiTableId.of("MyIngress.RID_forward");
        //匹配的key
        final PiMatchFieldId ridMatchFieldId = PiMatchFieldId.of("meta.myrid");
        final PiCriterion match = PiCriterion.builder()
                .matchExact(ridMatchFieldId,rid)
                .build();

        //action的参数
        final PiActionParamId port = PiActionParamId.of("port");
        final PiActionParam portParam = new PiActionParam(port, (short)portNumber.toLong());

        //创建anction
        final PiActionId ingressActionId = PiActionId.of("MyIngress.rid_forward");
        final PiAction action = PiAction.builder()
                .withId(ingressActionId)
                .withParameter(portParam)
                .build();

        //insertPiFlowRule(deviceId, enable_rid, match, action);
        insertPiFlowRulemakeTemporary(deviceId, enable_rid, match, action);
        log.info("*****TABLE change_dst Inserting rule on switch {}: table={}, match={}, action={}",
                deviceId, enable_rid, match, action);
    }
    private void insertPiFlowRulemakeTemporary(DeviceId switchId, PiTableId tableId,
                                               PiCriterion piCriterion, PiAction piAction) {
        FlowRule rule = DefaultFlowRule.builder()
                .forDevice(switchId)
                .forTable(tableId)
                .fromApp(appId)
                .withPriority(FLOW_RULE_PRIORITY)
                .makeTemporary(7200)
                .withSelector(DefaultTrafficSelector.builder()
                        .matchPi(piCriterion).build())
                .withTreatment(DefaultTrafficTreatment.builder()
                        .piTableAction(piAction).build())
                .build();
        flowRuleService.applyFlowRules(rule);
    }

}
///////////////////////////////////////////////////////////////////////////////////////////////////////


