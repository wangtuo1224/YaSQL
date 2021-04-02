const route = {
  name: 'redisms',
  path: 'redisms',
  component: () => import('./index.vue'),
  redirect: { name: 'redisms.list' },
  meta: { title: 'Redis管理', keepAlive: true, icon: 'sync' },
  children: [
    {
      name: 'redisms.list',
      path: '/redisms/list',
      component: () => import('./List/index.vue'),
      meta: { title: 'Redis概览', keepAlive: true, icon: 'search' },
    }
  ],
}

export default route