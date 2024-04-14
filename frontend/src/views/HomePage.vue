<template>
  <div class="relative min-h-screen flex flex-col items-center justify-center">

    <video autoplay muted loop id="homeVideo" class="absolute top-0 left-0 w-full h-full object-cover">
      <source src="@/assets/HomePageVideo.mp4" type="video/mp4">
      Your browser does not support HTML5 video.
    </video>

    <div class="absolute top-0 left-0 w-full h-full bg-black opacity-50"></div>

    <div class="z-10 w-full max-w-4xl px-10 py-8 mb-4 bg-white border-4 border-gray-200 rounded-lg shadow-lg">
      <h2 class="text-3xl font-extrabold text-center text-gray-900">
        Distributed Social Networking
      </h2>
      <p class="mt-2 text-sm text-center text-gray-600">
        Join our community of social media enthusiasts.
      </p>
      <div class="mt-6 flex justify-center">
        <RouterLink to="/signin"
          class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 mx-2">
          Log In
        </RouterLink>
        <RouterLink to="/signup"
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 mx-2">
          Sign Up
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
#homeVideo {
  position: fixed;
  right: 0;
  bottom: 0;
  min-width: 100%;
  min-height: 100%;
  z-index: -1;
}

/* Adjust the z-index to keep the video behind other content */
.content {
  z-index: 1;
}

/* Additional styles to increase the border and adjust the width */
.max-w-4xl {
  max-width: 1024px;
}

.border-4 {
  border-width: 4px;
  /* This increases the border size */
}

@media (min-width: 720px) {
  .max-w-4xl {
    padding: 8rem;
    /* Adjust padding for larger screens if needed */
  }
}
</style>
