<template>
    <div>
        <!-- Top Navigation Bar -->
        <nav class="py-10 px-8 border-b border-gray-200">
            <div class="max-w-10xl mx-auto flex justify-between items-center">
                <div>
                    <router-link to="/stream" class="text-xl"><strong>ARE YOU HTTP?</strong></router-link>
                </div>
                <div>
                    <button @click="logout" class="logout-button">Logout</button>
                </div>
            </div>
        </nav>

        <div class="flex-container">
            <!-- Side Navigation Bar -->
            <LeftSideNavBar class="left-side-nav" />

            <!-- Main Content -->
            <main class="main-content">
                <slot></slot>
            </main>
        </div>
    </div>
</template>

<script>
import LeftSideNavBar from './SideNavBar.vue';

export default {
    components: {
        LeftSideNavBar,
    },
    methods: {
        logout() {
            // Implement logout logic here
            console.log("User logged out");
            this.$router.push('/signin');
        },
    },
};
</script>


<style scoped>
.nav-bar {
    padding: 10px 8px;
    border-bottom: 1px solid #eaeaea;
}

.logout-button {
    padding: 8px 25px;
    background-color: #000000;
    color: #fff;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.logout-button:hover {
    background-color: #333333;
}

.text-xl {
    font-size: 1.25rem;
}

/* Parent container holding the side nav and the main content */
.flex-container {
    display: flex;
    flex-direction: row;
}

/* Left Side navigation styling */
.left-side-nav {
    flex: 0 0 auto;
    /* retain its size */
    width: 350px;
    padding: 20px;

}

/* Main content styling */
.main-content {
    flex-grow: 1;
    padding: 20px;
}
</style>