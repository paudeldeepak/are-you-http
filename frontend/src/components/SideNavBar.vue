<template>
    <div class="navbar-left">
        <div v-if="!isProfilePage" class="profile-display">
            <img :src="fullPictureUrl" alt="Profile Picture" class="profile-picture" />
            <h2 class="profile-name-left-side"><strong>{{ profile.displayName }}</strong><br />@{{ profile.username }}</h2>

        </div>

        <div class="column1">
            <nav>
                <ul class="list-none">
                    <li class="list-item">
                        <router-link to="/stream"> <i class="fas fa-home"></i> Home </router-link>
                    </li>

                    <li :class="{ 'active-nav-item': isProfilePage }" class="list-item">
                        <router-link :to="`/profile/${this.authorId}`">
                            <i class="fas fa-user"></i>
                            My Profile
                        </router-link>
                    </li>
                    <li :class="{ 'active-nav-item': isInboxPage }" class="list-item">
                        <router-link :to="`/inbox/${this.authorId}`">
                            <i class="fas fa-inbox"></i> 
                            Inbox
                        </router-link>
                    </li>
                    <li class="list-item">
                        <router-link to="/connections"> <i class="fas fa-users"></i> Connections </router-link>
                    </li>

                    <li v-if="!isCreatePostPage" class="list-item-create-post">
                        <router-link to="/create-post">
                            <i class="fa-solid fa-pen-nib"></i> Create Post
                        </router-link>
                    </li>
                </ul>
            </nav>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            HOST_URL: import.meta.env.VITE_API_URL,
            authorId: '', // Will be set dynamically from localStorage 
            profile: {
                picture: '',
                displayName: '',
                username: '',
            },
            defaultImage: "https://via.placeholder.com/150",
        };
    },
    computed: {
        fullPictureUrl() {
            return this.profile.picture || this.defaultImage;
        },
        isProfilePage() {
            return this.$route.name === 'profile';
        },
        isCreatePostPage() {
            return this.$route.name === 'create-post';
        },
        isInboxPage() {
            return this.$route.name === 'inbox';
        },
    },
    async created() {
        this.initializeAuthorId();
        if (this.authorId) {
            await this.fetchUserProfile();
        } else {
            console.error("Author ID is required but was not found.");
            // Handle the lack of authorId as needed, redirect to login
            this.$router.push('/signin');
        }
    },
    methods: {
        initializeAuthorId() {
            // Attempt to get the authorId from localStorage
            const storedAuthorId = localStorage.getItem('userId');
            if (storedAuthorId) {
                this.authorId = storedAuthorId;
            } else if (this.$route.params.authorId) {
                // If not found in localStorage, try to get it from the route params
                this.authorId = this.$route.params.authorId;
            } // No else clause needed, as there's no fallback ID
        },
        async fetchUserProfile() {
            console.log(this.authorId); // Use 'this' to access authorId
            if (!this.authorId) {
                console.error("No author ID found.");
                return;
            }
            try {
                const authToken = localStorage.getItem('userToken');
                if (!authToken) {
                    console.error("Authentication token not found.");
                    return;
                }
            const response = await axios.get(`${this.HOST_URL}/authors/${this.authorId}/`, {
            headers: {
                'Authorization': `Token ${authToken}`,
            },
        });
        this.profile = {
            picture: response.data.profileImage,
            displayName: response.data.displayName,
            username: response.data.username,
            github: response.data.github,
            id: this.authorId,
        };
        console.log('Fetched user profile:', this.profile);
    } catch (error) {
        console.error("Error fetching user profile:", error);
    }
},

        },
    };
</script>

<style scoped>
.navbar-left {
    flex: 1;
    margin: 20px;
    border-radius: 8px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    position: sticky;
    top: 10px;
    align-items: center;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border: 1px solid #ccc;
}

.profile-display {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    margin-bottom: 20px;
}

.profile-picture {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #fff;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 10px;
}

.profile-name-left-side {
    font-size: 20px;
    color: #333;
    margin-bottom: 5px;
}

.profile-username {
    color: #555;
    font-size: 18px;
}

.column1 {
    padding: 15px;
}

.list-item {
    font-size: x-large;
    font-weight: 500;
    background-color: #b6e1fe;
    padding: 15px;
    margin-left: 0px;
    margin-bottom: 10px;
    border-radius: 50px;
    text-align: center;
    box-shadow: 0 8px 10px rgba(0, 0, 0, 0.1);
}

.list-item-create-post {
    font-size: x-large;
    font-weight: 500;
    background-color: #54bbff;
    padding: 15px;
    margin-left: 0px;
    margin-bottom: 10px;
    border-radius: 50px;
    text-align: center;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.list-item:hover,
.list-item-create-post:hover {
    background-color: #a3cbed;
}
</style>