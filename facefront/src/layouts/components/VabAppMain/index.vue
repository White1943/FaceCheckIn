<template>
  <div v-if="routerView" class="app-main-container">
    <vab-github-corner />
    <transition mode="out-in" name="fade-transform">
      <keep-alive :include="cachedRoutes" :max="keepAliveMaxNum">
        <router-view :key="key" class="app-main-height" />
      </keep-alive>
    </transition>
    <footer v-show="footerCopyright" class="footer-copyright">
      Copyright
      <vab-icon :icon="['fas', 'copyright']"></vab-icon>
      vue-admin-better 开源免费版 {{ fullYear }}
    </footer>
  </div>
</template>

<script>
  import { mapActions, mapGetters } from 'vuex'
  import { copyright, footerCopyright, keepAliveMaxNum, title } from '@/config'

  export default {
    name: 'VabAppMain',
    data() {
      return {
        show: false,
        fullYear: new Date().getFullYear(),
        copyright,
        title,
        keepAliveMaxNum,
        routerView: true,
        footerCopyright,
      }
    },
    computed: {
      ...mapGetters({
        visitedRoutes: 'tabsBar/visitedRoutes',
        device: 'settings/device',
      }),
      cachedRoutes() {
        const cachedRoutesArr = []
        this.visitedRoutes.forEach((item) => {
          if (!item.meta.noKeepAlive) {
            cachedRoutesArr.push(item.name)
          }
        })
        return cachedRoutesArr
      },
      key() {
        return this.$route.path
      },
    },
    watch: {
      $route: {
        handler(route) {
          if ('mobile' === this.device) this.foldSideBar()
        },
        immediate: true,
      },
    },
    created() {
      const handleReloadRouterView = () => {
        this.routerView = false
        this.$nextTick(() => {
          this.routerView = true
        })
      }

      //重载所有路由
      this.$baseEventBus.$on('reload-router-view', handleReloadRouterView)

      this.$once('hook:beforeDestroy', () => {
        this.$baseEventBus.$off('reload-router-view', handleReloadRouterView)
      })
    },
    mounted() {},
    methods: {
      ...mapActions({
        foldSideBar: 'settings/foldSideBar',
      }),
    },
  }
</script>

<style lang="scss" scoped>
  .app-main-container {
    position: relative;
    width: 100%;
    overflow: hidden;

    .vab-keel {
      margin: $base-padding;
    }

    .app-main-height {
      min-height: $base-app-main-height;
    }

    .footer-copyright {
      min-height: 55px;
      line-height: 55px;
      color: rgba(0, 0, 0, 0.45);
      text-align: center;
      border-top: 1px dashed $base-border-color;
    }
  }
</style>
