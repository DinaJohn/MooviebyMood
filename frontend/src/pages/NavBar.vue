<template>
  <div class="nav-container">
    <nav class="navbar navbar-expand-lg bg-body-tertiary" >
      <div class="container-fluid">
        <div class="logo-cont" :class="{ 'animate': isAnimating }">
          <img src="@/assets/LogoSVG.svg" alt="Logo">
        </div>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNavDropdown">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <slot name="reset-button" class="nav-link"></slot>
            </li>
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                Recommendations
              </a>
              <ul class="dropdown-menu">
                <li><router-link :to="{ name: 'Score-Tag based Recommendations' }" class="dropdown-item">Score and Tag-based Recommendations</router-link></li>
                <li><router-link :to="{ name: 'Tag-based Recommendations' }" class="dropdown-item">Tag-based Recommendations</router-link></li>
              </ul>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'About' }" class="nav-link">About</router-link>
            </li>
            <li class="nav-item">
              <router-link :to="{ name: 'Logout' }" class="nav-link">Logout</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'Navbar',
  setup() {
      const isAnimating = ref(true);

      return {
          isAnimating
      };
  }
});
</script>

<style scoped>
.nav-container {
  align-self: flex-start; 
  justify-self: flex-start; 
  position: sticky;
  top: 0;
  z-index: 10;
  margin: 2em;
  
}

.container-fluid{
  margin: 0 auto;
  background-color: black;
}

.bg-body-tertiary{
  padding-top: 0%;
  padding-bottom: 0%;
}

.navbar-toggler{
  border-color: azure;
  background-color: #8F86E3;
  box-shadow: 0px 4px 8px rgba(57, 9, 172, 1); 
}

img{
  height: 10vh;
}

.animate {
    animation: rotate 5s linear infinite;
}

.navbar-nav .nav-item .nav-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: color 0.3s ease-in-out; 
  font-family: "Abril Fatface", serif;
  color: #ffffff;
  font-size: 3rem;
}

.dropdown-menu{
  font-family: "Abril Fatface", serif;
  color: #ffffff;
  font-size: 2rem;
}

.navbar-nav .nav-item{
  font-family: 'Lucida Sans', 'Helvetica', 'Arial', 'sans-serif';
  font-weight: bolder;
  font-size: x-large;
  margin-right: 3rem;
} 

.nav-link:hover {
  color: #FDC128 !important;
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
