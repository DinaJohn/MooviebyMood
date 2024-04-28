<template>
  <div class="main-container">
    <NavBar>
      <template v-slot:reset-button>
        <!-- The button will only be shown if a mood is selected -->
        <button v-if="selectedMood" class="nav-link" @click="resetPage">Reset</button>
      </template>
    </NavBar>
    <!-- Bootstrap Carousel for Moods and Recommendations -->
    <div id="selectionCarousel" class="carousel-slide">
      <div class="carousel-inner">
        <!-- For Mood Selection -->
        <div class="carousel-item" :class="{ active: currentIndex === 0 }">
          <div class="mood-selection-container">
            <h2>Select a mood:</h2>
            <div class="mood-buttons">
              <button class="mood-button" 
                      v-for="mood in moods" 
                      :key="mood" 
                      :class="mood.toLowerCase()" 
                      @click="handleMoodClick(mood)"
                      :disabled="isDisabled">
                {{ mood }}
              </button>
            </div>
          </div>
        </div>

        <div class="carousel-item recommendation-slide"  
            v-for="(rec, index) in recommendations" 
            :key="index"
            :class="{ active: currentIndex === index + 1 }">
          <div class="d-block w-100 recommendation-container" v-if="rec.details">
            <div class="movie-card">
              <h3 class="movie-card-title">{{ rec.details.title }}</h3>
              <div class="movie-details"> 
                <div class="poster-container">
                  <img class="movie-poster" :src="'https://image.tmdb.org/t/p/w500' + rec.details.poster_path" alt="Movie Poster" />
                  <div class="movie-interactions">
                    <button @click="() => handleUserAction('Like', index)" :disabled="rec.interacted">
                      Like
                    </button>
                    <button @click="() => handleUserAction('Dislike', index)" :disabled="rec.interacted">
                      Dislike
                    </button>
                    <button @click="() => handleUserAction('Perfect', index)" :disabled="rec.interacted">
                      Perfect
                    </button>
                  </div>
                </div>
                <div class="movie-info">
                  <!-- Displaying the video -->
                  <div class="movie-trailer" v-if="rec.details.video">
                    <LiteYouTubeEmbed
                      :id="rec.details.video.key"
                      :title="rec.details.video.name"
                    />
                  </div>
                  <div class="movie-overview">
                    <p>{{ rec.details.overview }}</p>
                    <p v-if="rec.details.genres"><span class="headers">Genres: &ensp;</span>{{ rec.details.genres.map(genre => genre.name).join(', ') }}</p>
                    <p><span class="headers">Release Date: &ensp;</span> {{ rec.details.release_date }}</p>
                    <p><span class="headers">Runtime: &ensp;</span> {{ rec.details.runtime }} minutes</p>

                    <!-- Displaying up to two reviews -->
                    <div v-if="rec.details.reviews && rec.details.reviews.length">
                      <h4><span class="headers">Reviews: &ensp;</span></h4>
                      <ul class="reviewInfo">
                        <li v-for="(review, idx) in rec.details.reviews" :key="idx">
                          "{{ review.content.replace(/[_*]/g, '') }}" - <a :href="review.url" target="_blank">Read more</a>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Slide for 'Perfect' message -->
        <div class="carousel-item perfect-message-slide" v-if="perfectSelected" :class="{ active: currentIndex === recommendations.length + 1 }">
          <div class="d-block w-100 recommendation-container">
            <div class="final-message-section">
              <p>{{ typewriterText }}<span class="cursor">|</span></p>
            </div>
          </div>
        </div>
      </div>

      <!-- Controls for Carousel -->
      <button class="carousel-control-prev" type="button" data-bs-target="#selectionCarousel" data-bs-slide="prev" @click="prevSlide">
        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
      </button>
      <button class="carousel-control-next" type="button" data-bs-target="#selectionCarousel" data-bs-slide="next" @click="nextSlide">
        <span class="carousel-control-next-icon" aria-hidden="true"></span>
      </button>
    </div>
  </div>
</template>



<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import NavBar from './NavBar.vue';
import { useAuthStore, getCsrfToken } from '../store/User_auth';
import LiteYouTubeEmbed from 'vue-lite-youtube-embed'
import 'vue-lite-youtube-embed/style.css'

interface ReviewResult {
  author: string;
  content: string;
  url: string;
  id: string;
}

interface VideoResult {
  name: string;
  key: string;
  site: string;
  type: string;
  official: boolean;
  id: string;
}

interface MovieDetails {
  poster_path: string;
  title: string;
  overview: string;
  genres: { id: number; name: string }[];
  release_date: string;
  runtime: number;
  reviews: ReviewResult[]; 
  video: VideoResult | null;
}

interface Recommendation {
  movie: string;
  message: string;
  interacted?: boolean;
  final?: boolean;
  details?: MovieDetails;
}

export default defineComponent({
  name: 'MoodSelector',
  components: {
    NavBar,
    LiteYouTubeEmbed,
  },
  setup() {
    const authStore = useAuthStore();
    const moods = ref<string[]>(['Joy', 'Sadness', 'Anger', 'Fear', 'Disgust']);
    const selectedMood = ref<string>('');
    const recommendations = ref<Recommendation[]>([]);
    const isDisabled = ref(false);
    const perfectSelected = ref(false);
    const typewriterText = ref<string>('');
    const speed = 150; 
    const pause = 1000;
    const message = 'Thank you for using the recommendation system. Enjoy your movie!';

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

    const handleMoodClick = (mood: string) => {
      if (!isDisabled.value) {
        selectedMood.value = mood;
        isDisabled.value = true;
        console.log('Buttons should now be disabled');
        fetchRecommendation();
      }
    };

    const fetchRecommendation = async () => {
      if (!authStore.user?.username) {
        console.error('User is not authenticated.');
        recommendations.value.push({ movie: '', message: 'Please login to continue.' });
        nextSlide();
        return;
      }

      if (!selectedMood.value) {
        alert('Please select a mood first.');
        return;
      }

      try {
        const response = await fetch('http://localhost:8000/api/mood_selection_content_recommendation/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
          },
          body: JSON.stringify({ mood: selectedMood.value, userId: authStore.user.username,  }),
        });

        if (!response.ok) {
          throw new Error('Failed to fetch recommendations');
        }

        const data = await response.json();
        console.log(data)
        if (data.status === 'success' && data.recommendation) {
          const details = data.details;
          const video = details.videos.results.length > 0 ? details.videos.results[0] : null;
          const reviews = details.reviews.results.slice(0, 2);
          console.log(details)

          recommendations.value.push({ movie: data.recommendation, message: '', details: {
            ...details,
            video, 
            reviews 
          }});
          nextSlide();
        } 
        else {
          recommendations.value.push({ movie: '', message: data.message || 'No recommendations found.' });
          nextSlide();
        }
      } 
      catch (error) {
        console.error('Error fetching recommendations:', error);
        recommendations.value.push({ movie: '', message: 'Error fetching recommendations. Please try again later.' });
        nextSlide();
      } 
      finally {
        isDisabled.value = true;
      }
    };

    const handleUserAction = async (action: string, index: number) => {
      if (!authStore.user?.username) {
        console.error('User is not authenticated.');
        recommendations.value.push({ movie: '', message: 'Please login to continue.' });
        nextSlide();
        return;
      }

      try {
        console.log(recommendations.value[index])
        const response = await fetch('http://localhost:8000/api/user_action_on_recommendation/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
          },
          body: JSON.stringify({
            action: action,
            movieTitle: recommendations.value[index].movie,
            userId: authStore.user.username,
            mood: selectedMood.value,
            type: 'tag',
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to process user action');
        }

        const data = await response.json();
        console.log(data)
        if (data.status === 'success') {
          if (action === 'Perfect') {
            perfectSelected.value = true;
            nextSlide();
          } 
          else if (data.next_recommendation) {
            const details = data.details;
            const video = details.videos.results.length > 0 ? details.videos.results[0] : null;
            const reviews = details.reviews.results.slice(0, 2);

            recommendations.value.push({ movie: data.next_recommendation, message: '', details: {
              ...details, 
              video, 
              reviews
            }});
            nextSlide();
          } 
          else {
            recommendations.value[index].message = data.message || 'Thank you for using the recommendation system. Enjoy your movie!';
            nextSlide();
          }
        } 
        else {
          throw new Error(data.message || 'Failed to process user action');
        }
        recommendations.value[index].interacted = true;
      } 
      catch (error) {
        console.error('Error processing user action:', error);
        recommendations.value.push({ movie: '', message: 'Error processing action. Please try again later.' });
        nextSlide();
      }
    };
    
    const resetPage = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/refresh_recommendations/', {
          method: 'POST',  
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
          },
        });
        const data = await response.json();
        if (data.status === 'success') {
          console.log(data.message);
          selectedMood.value = '';
          recommendations.value = [];
          isDisabled.value = false;
          perfectSelected.value = false;
          currentIndex.value = 0;
        } 
        else {
          console.error('Failed to refresh recommendations:', data.message);
        }
      } 
      catch (error) {
        console.error('Error refreshing recommendations:', error);
      }
    };

    const currentIndex = ref(0); 

    const nextSlide = () => {
      if (currentIndex.value < recommendations.value.length + 1) {
        currentIndex.value++;
      } else {
        currentIndex.value = 0;
      }
    };

    const prevSlide = () => {
      if (currentIndex.value > 0) {
        currentIndex.value--;
      } else {
        currentIndex.value = recommendations.value.length + 1; 
      }    
    };

    onMounted(() => {
      typeWriterEffect();
    });

    return {
      moods,
      selectedMood,
      recommendations,
      isDisabled,
      handleMoodClick,
      handleUserAction,
      resetPage,
      perfectSelected,
      currentIndex,
      nextSlide,
      prevSlide,
      typewriterText,
    };
  },
});
</script>

<style scoped>
.nav-link {
  display: flex;
  align-items: center;
  gap: 1rem; 
  transition: color 0.3s ease-in-out;
  font-family: "Abril Fatface", serif;
  color: #4A29D7;
  font-size: 3rem;
}

.nav-link:hover {
  color: #8F86E3 !important;
}

.main-container {
  white-space: pre-wrap; 
  font-family: "Abril Fatface", serif;
  color: #ffffff;
  word-wrap: break-word;
}

#selectionCarousel {
  margin: 0 auto;
  margin-top: 1em;
  align-self: center; 
  justify-self: center;
  width: 85vw; 
  padding-bottom: 2em;
  padding-top: 2em;
  padding-left: 4em;
  padding-right: 4em;
  color: #fff; 
  border: 2px solid transparent;
  box-shadow: 
    0 0 5px #ff0000, 
    0 0 15px #ff4000, 
    0 0 30px #ff8000,
    0 0 60px #ffbf00, 
    0 0 90px #ffff00; 

  background: black;
  border-radius: 10px; 
}

h2, h3 {
  margin-bottom: 2rem;
  text-align: center;
  font-size: 8em;
}

h3{
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.mood-buttons {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 2rem;
  margin-bottom: 2rem;
}

.mood-button {
  background-color: #E17A00; 
  border: none;
  border-radius: 20px;
  padding: 0.5rem 1rem;
  font-size: 5em;
  cursor: pointer;
  transition: transform 0.3s ease;
  color: white;
  width: 60vw;
}

.mood-button:hover, .mood-button.selected {
  transform: scale(1.05);
  border-radius: 20px;
}

.mood-button.joy:hover, .mood-button.joy.selected {
  background-color: #8D5D39; 
  border: #3909AC solid 2px; 
}

.mood-button.sadness:hover, .mood-button.sadness.selected {
  background-color: #8D5D39;
  border: #3909AC solid 2px; 
}

.mood-button.anger:hover, .mood-button.anger.selected {
  background-color: #8D5D39; 
  border: #3909AC solid 2px; 
}

.mood-button.fear:hover, .mood-button.fear.selected {
  background-color: #8D5D39; 
  border: #3909AC solid 2px;
}

.mood-button.disgust:hover, .mood-button.disgust.selected  {
  background-color: #8D5D39; 
  border: #3909AC solid 2px;
}

.mood-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.movie-card {
  display: flex;
  flex-direction: column;
  color: #fff;
  gap: 1em;
  max-width: 80vw; 
  height: 80vh; 
  justify-content: flex-start; 
  position: relative; 
  padding: 1rem;
  align-items: flex-start;
  box-sizing: border-box;
  align-items: center;
  overflow: hidden; 
}

.movie-card-title {
  align-self: flex-start; 
  width: 100%; 
  padding-bottom: 1rem; 
}

.movie-details {
  flex: 1; 
  display: flex;
  flex-direction: row;
  justify-content: center;
  overflow-y: auto; 
  margin-left: 2em;
  width: calc(100% - 2em);
  margin: 0 auto;
  overflow: auto; 
  gap: 2em;
}

.movie-poster {
  display: flex;
  flex-direction: column;
  display: block;
  width: 100%;
  max-width: 100%;
  height: auto; 
}

.movie-interactions{
  display: flex;
  flex-direction: column;
  justify-content: center;
  font-size: 2em;
}

.movie-interactions button {
  width: auto;
  margin: 0.5rem;
  background-color: #FDC128;
  border-radius: 20px;
}


.movie-interactions button:hover, 
.movie-interactions button.selected {
  transform: scale(1.05);
  border-radius: 20px;
  background-color: #FFA53B;
  border: #3909AC solid 2px;
}

.movie-info {
  display: flex;
  flex-direction: column;
  text-align: left;
}

.movie-overview{
  display: flex;
  flex-direction: column;
  width: 50vw;
  font-size: 2em;
}

.headers, h4 .headers{
  color: #FDC128;
  font-size: 2rem;
}

.reviewInfo{
  font-style: italic;
  font-size: 1em;
  list-style-type: none; 
  padding-left: 0; 
  margin-left: 0; 
}

.final-message-section{
  font-size: 5em;
  align-items: center;
  justify-content: center;
  color: #FDC128;
  height: 70vh;
}

@media (max-width: 768px) {
  .mood-buttons, .actions {
    flex-direction: column;
    align-items: stretch;
  }

  .movie-card {
    padding: 0.5em; 
  }

  .movie-details {
    width: calc(100% - 1em); 
  }
}

.carousel-control-prev, .carousel-control-next {
  width: 4%; 
}

.carousel-control-prev-icon, .carousel-control-next-icon {
  background-size: 100%, 100%;
}

.carousel-item:not(.active) {
  display: none;
}

</style>

