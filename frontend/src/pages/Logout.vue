<template>
  <div>
    Logging you out...
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../store/User_auth';

export default defineComponent({
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    onMounted(() => {
      if (authStore.isLoggedIn){
        logout();
      }
    });

    const logout = async () => {
      const success = await authStore.logout(); 
      if (success) {
      router.push('/login'); 
      }
    };

    return {};
  },
});
</script>
