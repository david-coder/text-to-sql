#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/12 4:06 PM
# @Author  : baluobo
# @File    : table_schema.py
# @Description :

database_schema_string = """
CREATE TABLE `ecs_js.room_region_center2` (
  `room_id` bigint(20) DEFAULT NULL COMMENT '机房id',
  `node_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '机房名称',
  `region_id` bigint(20) DEFAULT NULL COMMENT '机楼id',
  `region_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '机楼名称',
  `date_center_id` bigint(20) DEFAULT NULL COMMENT '机房模式id',
  `room_mode` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '机房模式',
  `city_id` bigint(20) DEFAULT NULL COMMENT '城市id',
  `city` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT '' COMMENT '城市名称',
  `province_id` int(11) NOT NULL COMMENT '省份id',
  `province` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '省份名称'）
  COMMENT ON TABLE ecs_js.room_region_center2 IS '机房所处的省份以及机房所在机楼的信息表';


CREATE TABLE `ecs_js.dwd_strategy_data_di` (
  `source` varchar(64) DEFAULT NULL,
  `id` bigint(20) NOT NULL COMMENT '主键策略id',
  `device_id` bigint(20) DEFAULT NULL COMMENT '设备id',
  `signal_id` bigint(20) DEFAULT NULL COMMENT '信号量id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `strategy_name` varchar(256) DEFAULT NULL COMMENT '策略名称',
  `is_auto` tinyint(4) DEFAULT NULL COMMENT '是否是自动策略(0:不自动，1：自动)',
  `default_strategy_type` varchar(32) DEFAULT NULL COMMENT '策略类型(初始化/最大负载)',
  `remarks` text DEFAULT NULL COMMENT '说明',
  `creator_name` varchar(64) DEFAULT NULL COMMENT '创建者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `execute_time` datetime DEFAULT NULL COMMENT '执行时间',
  `is_deleted` tinyint(4) DEFAULT NULL COMMENT '是否删除(0：未删除，1：已删除)',
  `is_timing` tinyint(4) DEFAULT NULL COMMENT '是否启动定时',
  `retry_times` int(11) DEFAULT NULL COMMENT '重试次数',
  `fallback_style` varchar(255) DEFAULT NULL COMMENT '回退方式',
  `regulation` tinyint(4) DEFAULT NULL COMMENT 策略执行方式'1-智能策略，0-手动策略',
  `execute_status` tinyint(4) DEFAULT NULL COMMENT '执行状态',
  `schedule_job_id` int(11) DEFAULT NULL,
  `room_id` bigint(20) NOT NULL COMMENT '机房id',
  `source_strategy_id` int(11) DEFAULT NULL,
  `retry_interval` int(11) DEFAULT NULL COMMENT '重试间隔',
  `strategy_detail_name` varchar(128) DEFAULT NULL COMMENT '策略名称',
  `strategy_level` int(11) DEFAULT NULL COMMENT '策略优先级',
  `control_value` decimal(32,2) DEFAULT NULL COMMENT '调控值',
  `delete_time` datetime DEFAULT NULL COMMENT '删除时间',
  `metadata` varchar(128) DEFAULT NULL COMMENT '扩展字段',
  `room_name` varchar(2560) DEFAULT NULL COMMENT '机房名称',
  `device_name` varchar(2560) DEFAULT NULL COMMENT '设备名称',
  `signal_name` varchar(2560) DEFAULT NULL COMMENT '信号量名称',
  `new_strategy` varchar(128) DEFAULT NULL COMMENT '策略类型'（default:默认策略，saving：升温策略，lock：锁定策略，open：开机策略，cooling：降温策略，station：冷战策略，influence:影响力策略，close：关机策略）
  COMMENT ON TABLE ecs_js.dwd_strategy_data_di IS '机房中所生成的策略的信息表';
  
  
CREATE TABLE `ecs_js.res_alarm` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `alarm_id` bigint(20) DEFAULT NULL COMMENT '告警id',
  `alarm_target` varchar(64) DEFAULT NULL 告警目标,
  `alarm_object_id` bigint(20) DEFAULT NULL 告警实体id,
  `alarm_object_name` varchar(64) DEFAULT NULL 告警实体名称,
  `alarm_strategy_id` bigint(20) DEFAULT NULL 告警的策略id,
  `monitor_indicators` bigint(20) DEFAULT NULL COMMENT '监控指标',
  `monitor_type` tinyint(4) DEFAULT NULL COMMENT '1：系统告警 2：信号量告警',
  `alarm_type` tinyint(4) DEFAULT NULL COMMENT '1：通讯中断 2：数据异常',
  `alarm_level` tinyint(4) DEFAULT NULL COMMENT '1：严重 2：紧急 3：警告 4：消息',
  `strategy_type` tinyint(4) DEFAULT NULL COMMENT '0非智能策略，1智能策略',
  `current_value` varchar(64) DEFAULT NULL COMMENT '当前值',
  `alarm_status` tinyint(4) DEFAULT 0 COMMENT '0待确认，1已确认，2待办',
  `room_id` bigint(20) DEFAULT NULL COMMENT '机房id',
  `alarm_content` varchar(64) DEFAULT NULL COMMENT '告警描述',
  `system_id` int(11) DEFAULT NULL COMMENT 系统id,
  `remarks` varchar(255) DEFAULT NULL COMMENT '备注',
  `next_send_time` datetime DEFAULT NULL COMMENT '下次弹出时间',
  `send_counts` int(11) DEFAULT NULL COMMENT '弹出次数',
  `create_time` datetime DEFAULT current_timestamp() COMMENT '创建时间',
  `update_time` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '修改时间',
  `confirm_time` datetime DEFAULT NULL COMMENT 确认时间,
  `reserved_column` varchar(128) DEFAULT NULL,
  `operator` varchar(32) DEFAULT NULL COMMENT '操作人'）
  COMMENT ON TABLE ecs_js.res_alarm IS '机房中所生成告警信息表';
  
CREATE TABLE `ecs_js.dim_room_info_df` (
  `project_name` varchar(2560) DEFAULT NULL COMMENT '项目名称',
  `data_center_id` bigint(20) DEFAULT NULL COMMENT '数据中心id',
  `region_id` bigint(20) DEFAULT NULL COMMENT '机楼id',
  `room_id` bigint(20) DEFAULT NULL COMMENT '机房id',
  `province` varchar(128) DEFAULT NULL COMMENT '省',
  `city` varchar(256) DEFAULT NULL COMMENT '城市',
  `city_code` varchar(256) DEFAULT NULL COMMENT '城市id（平台内部统一）',
  `data_center_name` varchar(2560) DEFAULT NULL COMMENT '数据中心名称',
  `region_name` varchar(2560) DEFAULT NULL COMMENT '机楼名称',
  `room_name` varchar(2560) DEFAULT NULL COMMENT '机房名称（平台内部统一）',
  `room_volume` decimal(11,2) DEFAULT NULL COMMENT '机房体积',
  `room_area` decimal(11,2) DEFAULT NULL COMMENT '机房面积',
  `room_floor` decimal(11,2) DEFAULT NULL COMMENT '机房所在楼层',
  `rack_num` decimal(11,2) DEFAULT NULL COMMENT '机架数量',
  `ITDevice_load_rate` decimal(5,2) DEFAULT NULL COMMENT 'IT设备上架率',
  `cooling_type` varchar(256) DEFAULT NULL COMMENT '供冷类型',
  `target_saving_rate` decimal(5,2) DEFAULT NULL COMMENT '目标节能率',
  `it_type` varchar(256) DEFAULT NULL COMMENT '机房负载类型',
  `channel_type` varchar(256) DEFAULT NULL COMMENT '机房通道类型',
  `mix_channel_num` decimal(5,2) DEFAULT NULL COMMENT '混合通道数量',
  `cold_channel_num` decimal(5,2) DEFAULT NULL COMMENT '冷通道数量',
  `hot_channel_num` decimal(5,2) DEFAULT NULL COMMENT '热通道数量',
  `natural_cold_source` varchar(256) DEFAULT NULL COMMENT '机房内是否会利用新风或者自然冷源',
  `attention_reTemp_warning` varchar(256) DEFAULT NULL COMMENT '机房是否关注回风温度报警',
  `room_type` varchar(256) DEFAULT NULL COMMENT '机房类型',
  `climate_type` varchar(256) DEFAULT NULL COMMENT '机房所在气候区',
  `air_supply_mode` varchar(256) DEFAULT NULL COMMENT '送风方式'
  COMMENT ON TABLE ecs_js.dim_room_info_df IS '机房的维度表，记录了机房的静态信息';
  
CREATE TABLE `ecs_js.ecs_room_saving_day_di` (
  `room_id` bigint(20) NULL COMMENT '机房id',
  `T1_start_date` date NULL COMMENT 'T1开始时间',
  `T1_end_date` date NULL COMMENT 'T1结束时间',
  `insert_time` datetime NULL DEFAULT CURRENT_TIMESTAMP COMMENT '数据插入时间',
  `room_name` varchar(256) NULL COMMENT '机房名称',
  `T0_start_date` date NULL COMMENT 'T0开始时间',
  `T0_end_date` date NULL COMMENT 'T0结束时间',
  `PUE` DECIMAL(16, 2) NULL COMMENT '能耗比',
  `T0_power` DECIMAL(16, 2) NULL COMMENT 'T0用电量',
  `T1_power` DECIMAL(16, 2) NULL COMMENT 'T1用电量',
  `absolute_power` DECIMAL(16, 2) NULL COMMENT '绝对节电量',
  `saving_rate` DECIMAL(16, 2) NULL COMMENT '节能率',
  `T0_temperature_avg` DECIMAL(16, 2) NULL COMMENT 'T0时间段平均温度',
  `T1_temperature` DECIMAL(16, 2) NULL COMMENT 'T1时间温度')
  COMMENT ON TABLE ecs_js.ecs_room_saving_day_di IS '记录机房的节能率、PUE、绝对节电量表';

    CREATE TABLE ngfa.province_access (
    province_code VARCHAR(255) COMMENT '省份编码 AH:安徽,BJ:北京.....',
    province_name VARCHAR(255) COMMENT '省份名称 安徽,北京.....')  
    COMMENT ON TABLE ngfa.province_access IS "省份维度表"
    
    CREATE TABLE ngfa.man_idc_analysis_pt1h(
    
    `srcProvinceCode` VARCHAR(255) COMMENT '源端省份编码 AH:安徽,BJ:北京......',
    `dstProvinceCode` VARCHAR(255) COMMENT '目标端省份编码 AH:安徽,BJ:北京......',
    `srcCityCode` VARCHAR(255) COMMENT '源端城市编码',
    `dstCityCode` VARCHAR(255) COMMENT '目标端城市编码',
    `srcIdcUser` VARCHAR(255) COMMENT '源端客户编码,1:阿里,10034：腾讯,14:字节,10000:天翼云,10022:华为,10018:爱奇艺,10020:百度,8:北京首都在线,4:金山,5:京东,10026:快手,10028:美团,10526:网宿,9:网易',
    `dstIdcUser` VARCHAR(255) COMMENT '源端客户编码,1:阿里,10034：腾讯,14:字节,10000:天翼云,10022:华为,10018:爱奇艺,10020:百度,8:北京首都在线,4:金山,5:京东,10026:快手,10028:美团,10526:网宿,9:网易',
    `srcType` VARCHAR(255) COMMENT '源端类型 1:IDC,2:城域网,3:IDC客户,4:中国移动,5:中国联通,6:DNS,7:ITV,8:NOC,9:PT,10:QXZX,11:SOC,12:SW,13:WG,14:WLW,15:DX-YD',
    `dstType` VARCHAR(255) COMMENT '目标端类型 1:IDC,2:城域网,3:IDC客户,4:中国移动,5:中国联通,6:DNS,7:ITV,8:NOC,9:PT,10:QXZX,11:SOC,12:SW,13:WG,14:WLW,15:DX-YD',
    `inInterfaceType` VARCHAR(255) COMMENT '流入口类型 上行口：ut,下行口：dt,平行口:pt,其他口:ot',
    `outInterfaceType` VARCHAR(255) COMMENT '流出口类型 上行口：ut,下行口：dt,平行口:pt,其他口:ot',
    `routerProvince` VARCHAR(255) COMMENT '路由省份 AH:安徽,BJ:北京......',
    `routerType` VARCHAR(255) COMMENT '路由器类型：IDC,MAN(城域网)',
    `ipType` VARCHAR(255) COMMENT 'ip类型 0:ipv4,1:ipv6',
    `bytes` LARGEINT COMMENT '总bytes数，单位：Bytes',
    `flows` LARGEINT COMMENT '总flow数，单位：条',
    `packets` LARGEINT COMMENT '总包数，单位：个',
    timestamp DATETIME COMMENT '数据时间')
    COMMENT ON TABLE ngfa.man_idc_analysis_pt1h IS 'ngfa业务数据小时表'
"""

ngfa_database_schema_string = '''    
    CREATE TABLE ngfa.man_idc_analysis_pt1h(
    `srcProvinceCode` VARCHAR(255) COMMENT '源端省份编码 AH:安徽,BJ:北京......',
    `dstProvinceCode` VARCHAR(255) COMMENT '目标端省份编码 AH:安徽,BJ:北京......',
    `srcCityCode` VARCHAR(255) COMMENT '源端城市编码',
    `dstCityCode` VARCHAR(255) COMMENT '目标端城市编码',
    `srcIdcUser` VARCHAR(255) COMMENT '源端客户编码,1:阿里,10034：腾讯,14:字节,10000:天翼云,10022:华为,10018:爱奇艺,10020:百度,8:北京首都在线,4:金山,5:京东,10026:快手,10028:美团,10526:网宿,9:网易',
    `dstIdcUser` VARCHAR(255) COMMENT '源端客户编码,1:阿里,10034：腾讯,14:字节,10000:天翼云,10022:华为,10018:爱奇艺,10020:百度,8:北京首都在线,4:金山,5:京东,10026:快手,10028:美团,10526:网宿,9:网易',
    `srcType` VARCHAR(255) COMMENT '源端类型 1:IDC,2:城域网,3:IDC客户,4:中国移动,5:中国联通,6:DNS,7:ITV,8:NOC,9:PT,10:QXZX,11:SOC,12:SW,13:WG,14:WLW,15:DX-YD',
    `dstType` VARCHAR(255) COMMENT '目标端类型 1:IDC,2:城域网,3:IDC客户,4:中国移动,5:中国联通,6:DNS,7:ITV,8:NOC,9:PT,10:QXZX,11:SOC,12:SW,13:WG,14:WLW,15:DX-YD',
    `inInterfaceType` VARCHAR(255) COMMENT '流入口类型 上行口：ut,下行口：dt,平行口:pt,其他口:ot',
    `outInterfaceType` VARCHAR(255) COMMENT '流出口类型 上行口：ut,下行口：dt,平行口:pt,其他口:ot',
    `routerProvince` VARCHAR(255) COMMENT '路由省份 AH:安徽,BJ:北京......',
    `routerType` VARCHAR(255) COMMENT '路由器类型：IDC,MAN(城域网)',
    `ipType` VARCHAR(255) COMMENT 'ip类型 0:ipv4,1:ipv6',
    `bytes` LARGEINT COMMENT '总bytes数，单位：Bytes',
    `flows` LARGEINT COMMENT '总flow数，单位：条',
    `packets` LARGEINT COMMENT '总包数，单位：个',
    timestamp DATETIME COMMENT '数据时间')
    COMMENT ON TABLE ngfa.man_idc_analysis_pt1h IS 'ngfa业务数据小时表'

'''