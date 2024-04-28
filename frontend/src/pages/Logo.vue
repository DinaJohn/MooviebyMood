<template>
    <div class="logo-container" :class="{ 'animate': isAnimating }">
    </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

export default defineComponent({
    name: 'LogoPage',
    setup() {
        const router = useRouter();
        const isAnimating = ref(true);

        const transitionToLoginPage = () => {
            setTimeout(() => {
                router.push({ name: 'Login' });
            }, 4000); 
        };

        onMounted(() => {
            transitionToLoginPage();
        });

        return {
            isAnimating
        };
    }
});
</script>

<style scoped>
.logo-container {
  display: flex;
  justify-content: center;
  align-items: center; 
  height: 100vh; 
  width: auto; 
}

.animate {
    animation: rotate 5s linear infinite;
}

.logo-container {
  background-image: url('@/assets/LogoSVG.svg');
  background-size: 50%; 
  background-repeat: no-repeat;
  background-position: center;
}

@keyframes rotate {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}
</style>