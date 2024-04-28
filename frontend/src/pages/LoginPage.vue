<template>
  <div class="login_page">
    <img src='@/assets/LoginComp1.png' class="login_img">
    <div class="login_form">
      <p>{{ typewriterText }}<span class="cursor">|</span></p>
      <div v-if="showErrorModal" class="alert alert-danger d-flex align-items-center justify-content-center custom-alert" role="alert">
        <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Danger:">
          <use xlink:href="#exclamation-triangle-fill"/>
        </svg>
        <div>{{ errorMessage }}</div>
      </div>
      <svg xmlns="http://www.w3.org/2000/svg" class="d-none">
        <symbol id="exclamation-triangle-fill" viewBox="0 0 16 16">
          <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
        </symbol>
      </svg>
      <form @submit.prevent="login" class="d-flex flex-column align-items-center">
        <div class="form-floating mb-3">
          <input v-model="username" type="text" class="form-control" id="floatingUsername" placeholder="Username" />
          <label for="floatingUsername">Username</label>
        </div>
        <div class="form-floating mb-3">
          <input v-model="password" type="password" class="form-control" id="floatingPassword" placeholder="Password" />
          <label for="floatingPassword">Password</label>
        </div>
        <button type="submit" class="btn btn-outline-dark">Login</button>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useAuthStore } from '../store/User_auth';
import { useRouter } from 'vue-router';


export default defineComponent({
  setup() {
    const username = ref('');
    const password = ref('');
    const authStore = useAuthStore();
    const router = useRouter();
    const showErrorModal = ref(false);
    const errorMessage = ref('');
    const isAnimating = ref(true);
    const message = 'Login';
    const typewriterText = ref<string>('');
    const speed = 150; 
    const pause = 1000; 

        const transitionToLoginPage = () => {
            setTimeout(() => {
                router.push({ name: 'Login' });
            }, 4000); 
        };

    onMounted(() => {
      typeWriterEffect();
      transitionToLoginPage();
    });

    const typeWriterEffect = (index = 0) => {
      if (index < message.length) {
        typewriterText.value += message.charAt(index);
        setTimeout(() => typeWriterEffect(index + 1), speed);
      } else {
        setTimeout(() => {
          typewriterText.value = '';
          typeWriterEffect();
        }, pause);
      }
    };

    const login = async () => {
      const success = await authStore.login(username.value, password.value);
      try
      {
        if (success) {
          router.push('/about');
        }
        else{
          showErrorModal.value = true;
          errorMessage.value = 'Login failed. Please try again.';
        }
      }
      catch(err){
        showErrorModal.value = true;
        errorMessage.value = 'An error occurred during login.';
      }
    };

    return {
      username,
      password,
      login,
      showErrorModal,
      errorMessage,
      typewriterText,
      isAnimating
    };
  },
});
</script>


<style scoped>
.login_page {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  overflow-y: scroll;
}

.login_img{
  width: auto;
  height: 80vh;
}

.login_form {
  max-width: 400px; 
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.cursor {
  animation: blink 1s step-end infinite;
}

p {
  white-space: pre;
  font-family: "Abril Fatface", serif;
  color: #ffffff;
  font-size: 10rem;
}

input[type="text"],
input[type="password"]{
  color: #4F3D7A;
  padding: 0.75rem;
  margin-bottom: 1rem;
  border: 1px solid #ccc; 
  border-radius: 4px;
  background: #ffffff; 
  box-shadow: inset 0 1px 2px rgba(57, 9, 172, 1);
  width: 10vw;
  height: 5vh;
  font-size: x-large;
}

.custom-alert {
  margin: 2rem;
  text-align: center; 
  padding: 15px;
  border-radius: 5px;
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
}

button {
  padding: 0.5rem 1rem; 
  width: 4vw;
  height: 4vh;
  width: 100%; 
  height: auto; 
  padding: 10px; 
}

.btn.btn-outline{
  background-color: #FDC128;
}

.btn.btn-outline-dark{
  background-color: #FDC128;
  font-weight: bolder;
  font-size: x-large;
   width: auto;
  height: auto; 
  padding: 0.75rem 1.5rem;
}

</style>
