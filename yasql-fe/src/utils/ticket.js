export const TicketActState = [
    { key: 1, value: '进行中' },
    { key: 2, value: '已通过' },
    { key: 3, value: '已拒绝' },
    { key: 4, value: '已完成' },
    { key: 5, value: '已失败' },
    { key: 6, value: '已关闭' },
    { key: 7, value: '已中止' },
]

export const TicketAct = [ 
    { key: 1, value: '我发起的' },
    { key: 2, value: '待我处理' },
    { key: 3, value: '我已处理' },
    { key: 4, value: '我的全部' },
]

export const StateType = [
    {"key": 0, "value": "普通类型"},
    {"key": 1, "value": "初始状态"},
    {"key": 2, "value": "结束状态"},
]

export const DistributeType = [
    {"key": "any", "value": "其中之一"},
    {"key": "all", "value": "所有人"},
]

export const ParticipantType = [
    {"key": 1, "value": "个人"},
    {"key": 2, "value": "多人"},
    {"key": 3, "value": "部门"},
    {"key": 4, "value": "角色"},
    {"key": 5, "value": "机器人"},
    {"key": 6, "value": "工单字段"},
    {"key": 7, "value": "Hook"},
]

export const TransitionType = [
    {"key": 1, "value": "常规流转"},
    {"key": 2, "value": "其他"},
]

export const AttributeType = [
    {"key": 1, "value": "同意"},
    {"key": 2, "value": "拒绝"},
]