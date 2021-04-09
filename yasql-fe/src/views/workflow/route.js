const route = {
  name: 'workflow',
  path: '/workflow', 
  component: () => import('./index.vue'),
  redirect: { name: 'ticket.list' },
  meta: { title: '工单系统', icon: 'calendar' },
  children: [
    {
      name: 'ticket.summary',
      path: '/workflow/summary',
      component: () => import('./ticket/summary.vue'),
      meta: { title: '工单申请', icon: 'rocket' }
    },
    {
      name: 'ticket.new',
      path: '/workflow/ticket/:pk/new',
      hidden: true,
      props: true,
      component: () => import('./ticket/new.vue'),
      meta: { title: '创建工单', keepAlive: true }
    },
    {
      name: 'ticket.success',
      path: '/workflow/ticket/success',
      hidden: true,
      component: () => import('./ticket/success.vue'),
      meta: { title: '成功页面', keepAlive: true }
    },
    {
      name: 'ticket.list',
      path: '/workflow/ticket/list',
      component: () => import('./ticket/list.vue'),
      meta: { title: '工单审批', icon: 'rocket' }
    },
    {
      name: 'ticket.detail',
      path: '/workflow/ticket/detail/:pk',
      hidden: true,
      props: true,
      component: () => import('./ticket/detail.vue'),
      meta: { title: '工单详情', keepAlive: true }
    },
    {
      name: 'workflow.group',
      path: '/workflow/group/list',
      component: () => import('./group/list.vue'),
      meta: { title: '工单配置', icon: 'flag' },
    },
    {
      name: 'workflow.template.new',
      path: '/workflow/group/:pk/new',
      hidden: true,
      props: true,
      component: () => import('./config/new.vue'),
      meta: { title: '创建模版', keepAlive: true }
    },
    {
      name: 'workflow.template.detail',
      path: '/workflow/template/:pk',
      hidden: true,
      props: true,
      component: () => import('./config/detail.vue'),
      meta: { title: '模版详情', keepAlive: true }
    },
  ],
}
  
export default route