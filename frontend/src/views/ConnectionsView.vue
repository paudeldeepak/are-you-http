<template>

	<head>
		<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
		<link rel="stylesheet"
			href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css" />
	</head>
	<DefaultLayout>
		<div class="local-remote-users">
			<section class="local-users-section">
				<h3 class="section-title">Local Users</h3>
				<ul class="user-list">
					<li v-for="user in localUsers" :key="user.uid" class="user-item">
						<img :src="user.profileImage || defaultProfilePhoto" alt="Profile Photo" class="profile-photo">
						<div class="user-info">
							<h3>{{ user.displayName }}</h3>
							<p class="username">@{{ user.username }}</p>
							<span v-if="isFriend(user.uid)" class="friends-tag">Friend</span>
							<span v-else-if="isFollowing(user.uid)" class="following-tag">Following</span>
							<button v-if="!isFriend(user.uid) && !isFollowing(user.uid) && !isPending(user.uid)"
								@click="followUser(user.uid)" class="button follow-button">Follow</button>
							<button v-if="isFollowing(user.uid) || isFriend(user.uid)" @click="unfollowUser(user.uid)"
								class="button unfollow-button">Unfollow</button>
							<button v-if="isPending(user.uid)" class="button pending-button" disabled>Pending</button>
						</div>
					</li>
				</ul>
			</section>

			<section class="remote-users-section" v-for="(users, host) in remoteUsers" :key="host">
				<h3 class="section-title-remote">Remote Users @{{ host }}</h3>
				<ul class="user-list">
					<li v-for="user in users" :key="user.uid" class="user-item">
						<img :src="user.profileImage || defaultProfilePhoto" alt="Profile Photo" class="profile-photo">
						<div class="user-info">
							<h3>{{ user.displayName }}</h3>
							<p class="username">@{{ user.username }}</p>
							<p class="user-host">Host @{{ user.host }}</p>
							<span v-if="isFriend(user.uid)" class="friends-tag">Friend</span>
							<span v-else-if="isFollowing(user.uid)" class="following-tag">Following</span>
							<button v-if="!isFriend(user.uid) && !isFollowing(user.uid) && !isPending(user.uid)"
								@click="followUser(user.uid)" class="button follow-button">Follow</button>
							<button v-if="isFollowing(user.uid) || isFriend(user.uid)" @click="unfollowUser(user.uid)"
								class="button unfollow-button">Unfollow</button>
							<button v-if="isPending(user.uid)" class="button pending-button" disabled>Pending</button>
						</div>
					</li>
				</ul>
			</section>

		</div>
	</DefaultLayout>
</template>



<script>
import DefaultLayout from '@/components/DefaultLayout.vue';
import axios from 'axios';

export default {
	components: {
		DefaultLayout
	},
	data() {
		return {
			HOST_URL: import.meta.env.VITE_API_URL,
			followers: [],
			following: [],
			pendingRequests: [],
			friends: [],
			localUsers: [],
			remoteUsers: [],
		};
	},

	async created() {
		await this.fetchFollowers();
		await this.fetchFollowing();
		await this.fetchPending();
		await this.fetchFriends();
		await this.fetchAuthors();
		await this.checkFriendshipStatusRemote();
		await this.updateFollowRelationships();
		this.determineFriends();
		this.pollUpdates();
	},
	methods: {

		pollUpdates() {
			setInterval(async () => {
				await this.fetchFollowers();
				await this.fetchFollowing();
				await this.fetchPending();
				await this.fetchFriends();
				await this.checkFriendshipStatusRemote();
				await this.updateFollowRelationships();
				// await this.fetchAuthors();
				this.determineFriends();
			}, 5000);
		},

		isFollower(uid) {
			return this.followers.some(follower => follower.uid === uid);
		},

		isPending(userId) {
			return this.pendingRequests.includes(userId);
		},

		isFollowingBack(userId) {
			return this.followers.includes(userId) && !this.friends.includes(userId);
		},

		isFollowing(userId) {
			return this.following.some(follow => follow.uid === userId);
		},

		async fetchAuthors() {
			try {
				const currentUser = localStorage.getItem('userId');
				const authToken = localStorage.getItem('userToken');
				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				const response = await axios.get(`${this.HOST_URL}/authorsown/`, {
					headers: { 'Authorization': `Token ${localStorage.getItem('userToken')}` },
				});
				this.remoteUsers = {};
				response.data.items.forEach(author => {
					if (author.uid != currentUser) {
						if (author.is_remote) {
							if (!this.remoteUsers[author.host]) {
								this.remoteUsers[author.host] = [];
							}
							this.remoteUsers[author.host].push(author);
						} else {
							this.localUsers.push(author);
						}
					}
				});
			} catch (error) {
				console.error("Error fetching authors:", error);
			}
		},
		determineFriends() {
			console.log('friends array:', this.friends);
			const friendsUids = this.friends.map(friend => friend.uid);
			this.following = this.following.filter(following => !friendsUids.includes(following.uid));
		},


		isFriend(uid) {
			const isFriend = this.friends.some(friend => friend.uid === uid);
			console.log('isFriend:', isFriend);
			return isFriend;

		},

		async fetchPending() {
			try {
				const authorId = localStorage.getItem('userId');
				const authToken = localStorage.getItem('userToken');
				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				const response = await axios.get(`${this.HOST_URL}/authors/${authorId}/requests/pending`, {
					headers: { 'Authorization': `Token ${authToken}` },
				});
				this.pendingRequests = response.data.map(request => request.object.uid);
			} catch (error) {
				console.error("Error fetching pending requests:", error);
			}
		},

		async followUser(userId) {
			try {
				const currentUser = localStorage.getItem('userId');
				const authToken = localStorage.getItem('userToken');
				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				const followRequest = {
					type: 'Follow',
					summary: `${currentUser} wants to follow you.`,
					actor: {
						type: "author",
						id: `${this.HOST_URL}/authors/${currentUser}`,
						host: this.HOST_URL,
					},
					object: {
						type: "author",
						id: `${this.HOST_URL}/authors/${userId}`,
						host: this.HOST_URL,
					},
				};
				const response = await axios.post(`${this.HOST_URL}/authors/${userId}/inbox/`, followRequest, {
					headers: {
						Authorization: `Token ${authToken}`
					}
				});
				if (response.status === 200) {
					this.pendingRequests.push(userId);
					// Refetch friends to ensure data is up to date
					await this.fetchFriends();
				}
				console.log('Followed user:', response.data);
			} catch (error) {
				console.error('Error following user:', error);
			}
		},
		async unfollowUser(userId) {
			try {
				const authorId = localStorage.getItem('userId');
				const authToken = localStorage.getItem('userToken');
				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				const response = await axios.delete(`${this.HOST_URL}/authors/${userId}/followers/${authorId}`, {
					headers: {
						'Authorization': `Token ${authToken}`
					}
				});
				if (response.status === 204) {
					this.following = this.following.filter(follow => follow.uid !== userId);
					this.pendingRequests = this.pendingRequests.filter(request => request !== userId);
					// Refetch friends to ensure data is up to date
					await this.fetchFriends();
				}
				console.log("Friends after unfollowing:", this.friends);
			} catch (error) {
				console.error('Error unfollowing user:', error);
			}
		},

		async fetchFollowers() {
			try {
				const authorId = localStorage.getItem('userId');
				const authToken = localStorage.getItem('userToken');
				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				const response = await axios.get(`${this.HOST_URL}/authors/${authorId}/followers`, {
					headers: { 'Authorization': `Token ${authToken}` },
				});
				this.followers = response.data.items.map(item => ({
					uid: item.uid,
					username: item.username,
					displayName: item.displayName,
					profilePhoto: item.profileImage,
				}));
			} catch (error) {
				console.error('Error fetching followers:', error);
			}
		},

		async fetchFollowing() {
			try {
				const authorId = localStorage.getItem('userId');
				const authToken = localStorage.getItem('userToken');
				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				const response = await axios.get(`${this.HOST_URL}/authors/${authorId}/following/`, {
					headers: { 'Authorization': `Token ${authToken}` },
				});
				this.following = response.data.map(item => ({
					uid: item.object.uid,
					username: item.object.username,
					displayName: item.object.displayName,
					profilePhoto: item.object.profileImage,
				}));
			} catch (error) {
				console.error('Error fetching following:', error);
			}
		},
		async checkFriendshipStatusRemote() {
			try {
				const authToken = localStorage.getItem('userToken');
				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				const response = await axios.post(`checkForigenFollowing/`, {}, {
					headers: { 'Authorization': `Token ${authToken}` },
				});
				console.log('Friends response:', response.data);
			} catch (error) {
				console.error('Error fetching friends:', error);
			}
		},
		async updateFollowRelationships() {
			try {
				const authToken = localStorage.getItem('userToken');
				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				const response = await axios.post(`changeFollowStatus/`, {}, {
					headers: { 'Authorization': `Token ${authToken}` },
				});
				console.log('Updating Friends response:', response.data);
			} catch (error) {
				console.error('Error fetching friends:', error);
			}
		},
		async fetchFriends() {
			try {
				const authorId = localStorage.getItem('userId');
				const authToken = localStorage.getItem('userToken');
				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				const response = await axios.get(`${this.HOST_URL}/authors/${authorId}/friends/`, {
					headers: { 'Authorization': `Token ${authToken}` },
				});
				console.log('Friends response:', response.data);
				this.friends = response.data.filter(item => {
					// Ensure both users are following each other
					const friendId = item.object.uid;
					return this.following.some(follow => follow.uid === friendId) &&
						this.followers.some(follower => follower.uid === friendId);
				}).map(item => ({
					uid: item.object.uid,
					username: item.object.username,
					displayName: item.object.displayName,
					profilePhoto: item.object.profileImage,
				}));
			} catch (error) {
				console.error('Error fetching friends:', error);
			}
		},

	},
};
</script>

<style scoped>
.local-remote-users {
	display: flex;
	flex-direction: column;
	max-width: 800px;
	margin: 20px auto;
	padding: 20px;
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
	border-radius: 10px;
	background: #fff;
}

.section-title {
	font-size: 1rem;
	font-weight: bolder;
	color: #333;
	margin-bottom: 20px;
	padding: 15px 10px;
	background-color: #edede9;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08), 0 10px 20px rgba(0, 0, 0, 0.06), 0 2px 4px rgba(0, 0, 0, 0.07);
	border-radius: 5px;
	border: 1px solid #ddd;
	width: auto;
}

.user-list {
	list-style: none;
	margin: 0;
	padding: 0;
}

.user-item {
	display: flex;
	align-items: center;
	/* justify-content: space-between; */
	/* This was originally here, but commented out */
	padding: 10px;
	border-bottom: 1px solid #ddd;
	transition: background-color 0.2s ease;
}

.user-item:last-child {
	border-bottom: none;
}

.user-item:hover {
	background-color: #f9f9f9;
}

.profile-photo {
	border-radius: 50%;
	width: 50px;
	height: 50px;
	object-fit: cover;
	border: 2px solid #ddd;
	margin-right: 15px;
}

.user-info {
	flex-grow: 1;
	display: flex;
	flex-direction: column;
	align-items: flex-start;
}

.username {
	color: #555;
	font-size: 14px;
	margin-bottom: 4px;
}

.button {
	padding: 8px 16px;
	border-radius: 20px;
	border: none;
	cursor: pointer;
	font-size: 14px;
	font-weight: 600;
	transition: background-color 0.3s ease, color 0.3s ease;
}


.follow-button {
	font-size: 0.8em;
	color: white;
	margin-right: 7px;
	border-radius: 9px;
	padding: 4px 6px;
	background-color: #28a745;
	border: none;
	margin-top: -5px;
	margin-left: auto;
}

.follow-button:hover {
	background-color: #218838;
}

.section-title-remote {
	font-size: 1rem;
	font-weight: bolder;
	color: #333;
	margin-bottom: 20px;
	padding: 15px 10px;
	background-color: #edede9;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08), 0 10px 20px rgba(0, 0, 0, 0.06), 0 2px 4px rgba(0, 0, 0, 0.07);
	border-radius: 5px;
	border: 1px solid #ddd;
	width: auto;
}

.following-button i {
	color: #21a749;
}

.unfollow-button,
.delete-button {
	background-color: #f44336;
	color: white;
	margin-left: auto;
}

.unfollow-button:hover,
.delete-button:hover {
	background-color: #da190b;
}

.pending-button {
	font-size: 0.8em;
	color: #ffffff;
	margin-right: 7px;
	border-radius: 9px;
	padding: 4px 6px;
	background-color: #763180;
	margin-left: auto;
	/* Yellow color for pending */
}

.pending-button:hover {
	background-color: #4d0c58;
	/* Darker yellow color on hover */
}

.friends-tag {
	display: inline-block;
	background: #ffd700;
	color: black;
	border-radius: 4px;
	padding: 2px 6px;
	margin-left: 10px;
	font-size: 0.75rem;
	/* want the button to be right aligned */
}

/* New code to right align the buttons within the user-item */
.user-item {
	justify-content: space-between;
}

.setup-node-button {
	background-color: #4CAF50;
	color: white;
	border: none;
	padding: 8px 16px;
	border-radius: 20px;
	cursor: pointer;
	font-size: 14px;
	font-weight: 600;
	margin-bottom: 20px;
}

.setup-node-button:hover {
	background-color: #45a049;
}

.user-host {
	color: #555;
	font-size: 14px;
	margin-bottom: 4px;
}

.following-tag {
	display: inline-block;
	background: #007bff;
	color: white;
	border-radius: 4px;
	padding: 2px 6px;
	font-size: 0.75rem;
	margin-left: 10px;
}
</style>