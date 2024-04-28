<template>
  <div class="about-container">
    <div class="spotlight"></div>
    <div class="nav-bar">
      <NavBar />
    </div>
    
    <section ref="welcomeText" class="welcome-text">
        <p id="title">Moovie By Mood</p>
        <p>{{ typewriterText }}<span class="cursor">|</span></p>
    </section>

    <section ref="supportText" class="support-text">
        <p id="greta">"People watch movies emotionally."<br>-Greta Gerwig</p>
        <video src="@/assets/Greta.mp4" controls></video>
    </section>

    <section ref="aboutText" class="about-text">
      <img src="@/assets/aboutComp3.png" class="about-img" :class="{ 'animate': isAnimating }">
      <p id="about">There are <span class="color-changing">two</span> ways of recommending movies to users based on their mood.</p>
    </section>

    <section ref="typeText" class="type-text">
      <div class="score-box">
        <h3>SCORE+TAG</h3>
        <p>The first is based on the ratings and tags given to movies in the database.</p>
      </div>
      <div class="tag-box">
        <h3>TAG</h3>
        <p>The second is based on the tags given to movies in the database.</p>
      </div>
    </section>

    <section ref="aboutMoreText" class="about-text-more">
      <p>We suggest, you pick.</p>
    </section>
  </div>
</template>

<script lang="ts">
import NavBar from './NavBar.vue';
import { defineComponent, ref, onMounted, onUnmounted } from 'vue';

export default defineComponent({
  name: 'AboutComponent',
  components: {
    NavBar,
  },
  setup() {
    const welcomeText = ref<HTMLElement | null>(null);
    const supportText = ref<HTMLElement | null>(null);
    const aboutText = ref<HTMLElement | null>(null);
    const typeText = ref<HTMLElement | null>(null);
    const aboutMoreText = ref<HTMLElement | null>(null);
    const message = 'Together we find the movie you need.';
    const typewriterText = ref<string>('');
    const speed = 150; 
    const pause = 1000;
    const isAnimating = ref(true);

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          
          entry.target.classList.remove('active');
          if (entry.isIntersecting) {
            entry.target.classList.add('active');
          }
        });
      },
      {
        rootMargin: '0px',
        threshold: 0.5,
      }
    );

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

    onMounted(() => {
      if (welcomeText.value) observer.observe(welcomeText.value);
      if (supportText.value) observer.observe(supportText.value); 
      if (aboutText.value) observer.observe(aboutText.value);
      if (typeText.value) observer.observe(typeText.value);
      if (aboutMoreText.value) observer.observe(aboutMoreText.value);
      typeWriterEffect();
    });

    onUnmounted(() => {
      observer.disconnect();
    });

    return {
      welcomeText,
      supportText,
      aboutText,
      typeText,
      aboutMoreText,
      isAnimating,
      typewriterText,
    };
  },
});
</script>

<style scoped>
.about-container {
  z-index: 10;
  padding: 1em;
  display: flex;
  flex-direction: column;
  min-height: 100vh; 
}

.nav-bar {
  position: sticky; 
  top: 0em;
  width: 100%;
  z-index: 1000; 
  background-color: black;
}

section {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: opacity 0.5s ease-in-out, transform 0.5s ease-in-out;
  opacity: 0;
  visibility: hidden;
}

section.active {
  opacity: 1;
  visibility: visible;
}

.in-view {
  opacity: 1;
  transform: translateY(0);
  transition-delay: 0.3s; 
}

.welcome-text #title{
  font-size: 17rem; 
  animation: none;
}

p, h3 {
  white-space: pre-wrap;
  font-family: "Abril Fatface", serif;
  color: #ffffff;
  font-size: 5rem; 
  text-align: center;
  margin: 0 auto; 
  word-wrap: break-word;
}

@keyframes flickerAnimation {
  0%, 100% { opacity: 1; }
  10% { opacity: 0.8; }
  20% { opacity: 1; }
  30% { opacity: 0.6; }
  40% { opacity: 1; }
  50% { opacity: 0.7; }
  60% { opacity: 1; }
  70% { opacity: 0.5; }
  80% { opacity: 1; }
  90% { opacity: 0.9; }
}

.welcome-text {
  animation: flickerAnimation 10s infinite;
  display: flex;
  flex-direction: column;
  height: 75vh;
  background-image: url('@/assets/AboutComp2.png');
  background-repeat: no-repeat;
  background-position: center;
}

.support-text {
  display: flex;
  flex-direction: row; 
  justify-content: center; 
  align-items: center; 
  text-align: center;
  height: 100vh; 
  padding: 0 10px; 
  gap: 7em
}

.support-text video {
  max-width: 60%; 
  height: auto; 
}

#greta{
  width: 10em;
  margin: 0%;
  font-size: 6em; 
  background-image: url('@/assets/AboutComp7.png');
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
}

.about-text{
  gap: 7em
}

#about{
  width: 10em;
  margin: 0%;
  font-size: 6em; 
  text-align: end;
}

.animate {
    animation: rotate 10s linear infinite;
}

@keyframes rotate {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

.type-text {
  display: flex;
  flex-direction: row;
  height: 100vh;
  padding: 2em;
}

@keyframes colorChange {
  0% { color: #F540AD; }
  25% { color: #8D5D39; }
  50% { color: #FFA53B; }
  75% { color: #FDC128; }
  100% { color: #FF4772; }
}

.color-changing {
  animation: colorChange 2s infinite;
}

.score-box, .tag-box {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center; 
  align-items: center;
  margin: 3em;
  height: 75vh;
}

.score-box{
  background-image: url('@/assets/AboutComp4.png');
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
}

.tag-box{
  background-image: url('@/assets/AboutComp5.png');
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
}

.about-text-more{
  background-image: url('@/assets/AboutComp6.png');
  background-repeat: no-repeat;
  background-position: center;
  background-size: 60em;
}

@media (max-width: 768px) {
  p {
    font-size: 3rem; 
  }
}
</style>