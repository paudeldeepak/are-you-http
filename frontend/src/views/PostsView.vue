<template>
	<head>
		<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
		<link
			rel="stylesheet"
			href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css"
		/>
	</head>
	<DefaultLayout>
		<div class="create-post-container">
			<!-- Display Post Content -->
			<div v-if="post">
				<div class="post-header">
					<!-- Author's profile picture -->
					<img
						:src="post.author.profileImage || defaultProfilePhoto"
						alt="Author's Profile"
						class="author-profile-picture"
					/>
					<div class="post-info">
						<p class="post-username">
							<span>{{ post.author.username }} </span>
							<!-- Following sign/icon -->
							<span
								v-if="followedAuthors.includes(post.author.uid) && post.author.uid !== currentUser"
								class="following-icon"
							>
								<button class="following-button" disabled>
									<i class="fas fa-user-check"></i>
								</button>
							</span>
							<!-- Verification icon -->
							<i v-if="post.author.uid === currentUser" class="fas fa-check-circle verify-icon"></i>
						</p>
						<p class="post-timestamp">{{ publishedTimestamp }}</p>
					</div>
				</div>

				<div class="post-content">
					<h3 class="post-title">{{ post.title }}</h3>
					<div v-if="isImageContentType(post.contentType)">
						<img :src="post.content" alt="Post Image" class="post-image" />
					</div>
					<div
						v-else-if="post.contentType === 'text/markdown'"
						class="markdown-body"
						v-html="renderMarkdown(post.content)"
					></div>
					<p v-else>{{ post.content }}</p>
				</div>

				<div class="post-actions">
					<button
						@click="likePost(post)"
						:disabled="post.userHasLiked || isCurrentUserAuthor(post.author.uid)"
						:class="{ liked: post.userHasLiked, 'like-button': true }"
					>
						<i class="fa fa-heart"></i>&nbsp;{{ post.likesCount }}
					</button>
					<button
						@click="toggleCommentsSection(post)"
						class="view-comments-button"
						:class="{ active: post.showComments }"
					>
						<i class="fa-regular fa-comment"></i> {{ " " + post.count }}
					</button>
				</div>
				<div v-if="post.showComments" class="comments-section">
					<div v-if="post.commentsError" class="error-message">{{ post.commentsError }}</div>
					<template v-if="post.commentsLoaded">
						<div v-if="!post.comments.length">
							<p>No comments</p>
						</div>
						<div v-else>
							<div class="comment" v-for="comment in post.comments" :key="comment.id">
								<div class="post-header">
									<img
										:src="comment.author.profileImage || defaultImage"
										alt="Profile Picture"
										class="post-profile-picture"
									/>
									<div class="post-info">
										<p class="post-username">{{ comment.author.displayName }}</p>
										<p class="post-timestamp">{{ formatDate(comment.published) }}</p>
									</div>
								</div>
								<div
									v-if="comment.contentType === 'text/markdown'"
									class="markdown-body"
									v-html="renderMarkdown(comment.comment)"
								></div>
								<p v-else>{{ comment.comment }}</p>
								<button
									@click="likeComment(comment)"
									:disabled="comment.userHasLiked || isCurrentUserAuthor(comment.author.uid)"
									:class="{ liked: comment.userHasLiked, 'like-button': true }"
								>
									<i class="fa fa-heart"></i>&nbsp;{{ comment.likesCount }}
								</button>
							</div>
						</div>
						<div class="pagination-controls">
							<button
								v-if="post.pagination.currentPage > 1"
								@click="loadPreviousPage(post)"
								class="pagination-button"
							>
								Previous
							</button>
							<button
								v-if="post.pagination.hasNextPage"
								@click="loadNextPage(post)"
								class="pagination-button"
							>
								Next
							</button>
						</div>
					</template>
					<h3 class="comment-form-title">Write a new comment</h3>
					<div class="input-group">
						<textarea
							v-model="post.newComment"
							placeholder="Write a comment..."
							class="input-style"
						></textarea>
					</div>
					<div class="input-group">
						<select v-model="post.newCommentContentType" class="input-style">
							<option value="text/plain">Plain Text</option>
							<option value="text/markdown">Markdown</option>
						</select>
					</div>
					<button @click="submitComment(post)" class="submit-comment-button">Post Comment</button>
				</div>
			</div>
		</div>
		<!-- Modal component for sharing -->
		<Modal
			v-if="showModal"
			@close="showModal = false"
			@sharePost="handleSharePost"
			:authors="authors"
			:shareLink="shareLink"
			:visibility="currentPostVisibility"
			:postId="currentPostId"
		>
			<template v-slot:header> </template>
			<template v-slot:body>
				<!-- Content for the body slot, if needed -->
			</template>
		</Modal>
	</DefaultLayout>
</template>

<script>
import axios from "axios";
import DefaultLayout from "@/components/DefaultLayout.vue";
import { marked } from "marked";
import DOMPurify from "dompurify";
import Modal from "@/views/Modal.vue";

export default {
	components: {
		DefaultLayout,
		Modal,
	},
	data() {
		return {
			HOST_URL: import.meta.env.VITE_API_URL,
			userPosts: [],
			post: null, // Initialize post as null
			postId: this.$route.params.postId,
			authorUsername: "",
			authorProfilePicture: "",
			publishedTimestamp: "",
			followedAuthors: [],
			pendingRequests: [],
			friendsList: [],
			showModal: false,
			currentPostVisibility: "",
			currentPostId: null,
			targetAuthorId: null,
		};
	},
	computed: {
		currentUser() {
			return localStorage.getItem("userId");
		},
	},
	async created() {
		await this.fetchFriendsList();
		await this.fetchUserPosts();
		await this.fetchFollowingList();
		await this.fetchAuthors();
		await this.fetchPending();
		await this.sharePostWithAuthor();
	},
	methods: {
		constructCommentsUrl(authorId, postId, page) {
			return `${this.HOST_URL}/authors/${authorId}/posts/${postId}/comments?page=${page}`;
		},
		toggleCommentsSection(post) {
			post.showComments = !post.showComments;
			if (!post.commentsLoaded && post.showComments) {
				this.fetchComments(post);
			}
		},
		async fetchComments(post) {
			const commentsUrl = this.constructCommentsUrl(
				post.author.uid,
				this.getPostId(post.id),
				post.pagination.currentPage
			);

			try {
				const response = await axios.get(commentsUrl, {
					headers: {
						Authorization: `Token ${localStorage.getItem("userToken")}`,
					},
				});
				post.comments = response.data.comments;
				post.commentsLoaded = true;
				post.pagination.hasNextPage = post.pagination.currentPage < post.pagination.totalPages;

				for (let comment of post.comments) {
					await this.fetchLikesForComment(post, comment);
				}
				this.fetchUserLikes();
			} catch (error) {
				console.error("Error fetching comments:", error);
				post.commentsError = "Error fetching comments or you do not have permission.";
			}
		},

		loadNextPage(post) {
			if (post.pagination.hasNextPage) {
				post.pagination.currentPage++;
				this.fetchComments(post);
			}
		},
		loadPreviousPage(post) {
			if (post.pagination.currentPage > 1) {
				post.pagination.currentPage--;
				this.fetchComments(post);
			}
		},
		isCurrentUserAuthor(authorId) {
			const userId = localStorage.getItem("userId");
			return userId === authorId;
		},
		async submitComment(post) {
			if (!post.newComment.trim()) {
				alert("Comment cannot be empty!");
				return;
			}

			const authToken = localStorage.getItem("userToken");
			if (!authToken) {
				alert("You must be logged in to submit comments.");
				return;
			}

			// Adjusting the URL to match the provided pattern, assuming post.author.uid is the author's UUID
			const url = `${this.HOST_URL}/authors/${post.author.uid}/inbox/`;

			// Assuming you need to include the post's ID within the payload for backend processing
			const payload = {
				post_id: this.getPostId(post.id),
				comment: post.newComment,
				contentType: post.newCommentContentType,
				type: "comment",
				author: {
					type: "author",
					id: `${this.HOST_URL}/authors/${this.currentUser}`,
					host: this.HOST_URL,
				},
			};

			try {
				const response = await fetch(url, {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						Authorization: `Token ${authToken}`,
					},
					body: JSON.stringify(payload),
				});

				if (!response.ok) {
					throw new Error("Network response was not ok");
				}

				// Reset the new comment fields
				post.newComment = "";
				post.newCommentContentType = "text/plain";
				post.count += 1; // Assuming you're tracking comment count on the client

				// Update pagination if necessary, based on your frontend logic
				// Fetch the updated comments list to display the new comment
				this.fetchComments(post);

				alert("Comment successfully submitted!");
			} catch (error) {
				console.error("Error submitting comment:", error);
				alert("Failed to submit comment.");
			}
		},
		async fetchLikesForComment(post, comment) {
			const authToken = localStorage.getItem("userToken");
			try {
				const response = await axios.get(
					`${this.HOST_URL}/authors/${post.author.uid}/posts/${this.getPostId(
						post.id
					)}/comments/${this.getPostId(comment.id)}/likes`,
					{
						headers: {
							Authorization: `Token ${authToken}`,
						},
					}
				);
				comment.likesCount = response.data.length;
			} catch (error) {
				console.error("Error fetching likes for comment:", error);
			}
		},
		async fetchAllComments(postId, totalPages, authorId) {
			let allComments = [];
			for (let page = 1; page <= totalPages; page++) {
				const response = await axios.get(
					`${this.HOST_URL}/authors/${authorId}/posts/${postId}/comments?page=${page}`,
					{
						headers: { Authorization: `Token ${localStorage.getItem("userToken")}` },
					}
				);
				allComments = allComments.concat(response.data.comments);
			}
			return allComments;
		},
		async likeComment(comment) {
			// Construct the like object
			const likeObject = {
				summary: `${this.currentUser} Likes your comment`,
				type: "Like",
				author: {
					type: "author",
					id: `${this.HOST_URL}/authors/${this.currentUser}`,
					host: this.HOST_URL,
				},
				object: comment.id,
			};

			try {
				const response = await axios.post(`${this.HOST_URL}/authors/${comment.author.uid}/inbox/`, likeObject, {
					headers: {
						Authorization: `Token ${localStorage.getItem("userToken")}`,
					},
				});
				console.log("Like successful: ", response.data);
				comment.userHasLiked = true;
				comment.likesCount += 1;
			} catch (error) {
				console.error("Error sending like for comment: ", error);
			}
		},
		getPostId(postUrl) {
			return postUrl.substring(postUrl.lastIndexOf("/") + 1);
		},
		openShareModal(authorId, postId, visibility) {
			this.currentPostId = postId;
			this.shareLink = `${this.HOST_URL}/posts/${authorId}/${postId}`;
			this.showModal = true;
			this.currentPostVisibility = visibility;
		},

		async sharePostWithAuthor(postId, targetAuthorId) {
			const postToShare = this.userPosts.find((post) => this.getPostId(post.id) === postId);
			if (!postToShare) {
				return;
			}
			//do i include the sender receiver and whatever is in model??
			const senderId = this.currentUser;
			const receiverId = targetAuthorId;
			const totalCommentsCount = postToShare.count;
			const totalPages = Math.ceil(totalCommentsCount / 5); // Assuming 5 comments per page
			const allComments = await this.fetchAllComments(postId, totalPages, postToShare.author.uid);
			console.log("Post to share(likes):", postToShare.likes);
			console.log("Post to share(comments):", postToShare.comments);

			// Construct the JSON object to be sent
			const postData = {
				type: "post",
				title: postToShare.title,
				id: this.getPostId(postToShare.id),
				source: postToShare.source,
				origin: postToShare.origin,
				description: postToShare.description,
				contentType: postToShare.contentType,
				visibility: postToShare.visibility,
				content: postToShare.content,
				author: postToShare.author,
				sender: senderId,
				receiver: receiverId,
				likes: postToShare.likes,
				comments: allComments,
				shareLink: this.shareLink,
			};

			console.log(postData);
			console.log(postToShare);

			const targetUrl = `${this.HOST_URL}/authors/${targetAuthorId}/inbox/`;

			axios
				.post(targetUrl, postData, {
					headers: {
						Authorization: `Token ${localStorage.getItem("userToken")}`,
					},
				})
				.then((response) => {
					console.log("Post shared successfully:", response.data);
					alert("Post shared successfully!");
				})
				.catch((error) => {
					console.error("Error sharing post:", error);
					alert("Failed to share the post.");
				});
		},

		handleSharePost(selectedAuthors) {
			selectedAuthors.forEach((authorId) => {
				this.sharePostWithAuthor(this.currentPostId, authorId);
			});
		},

		async fetchAllComments(postId, totalPages, authorId) {
			let allComments = [];
			for (let page = 1; page <= totalPages; page++) {
				const response = await axios.get(
					`${this.HOST_URL}/authors/${authorId}/posts/${postId}/comments?page=${page}`,
					{
						headers: { Authorization: `Token ${localStorage.getItem("userToken")}` },
					}
				);
				allComments = allComments.concat(response.data.comments);
			}
			return allComments;
		},

		// Fetch all the users
		fetchAuthors() {
			this.isLoading = true;
			this.error = null;
			const authToken = localStorage.getItem("userToken"); // get stored token
			if (!authToken) {
				console.error("Authentication token not found.");
				this.error = "Authentication required.";
				this.isLoading = false;
				return;
			}
			axios
				.get("/authorsown/", {
					headers: {
						Authorization: `Token ${authToken}`, // include token in the request headers
					},
				})
				.then((response) => {
					this.authors = response.data.items;
				})
				.catch((error) => {
					console.error("Error fetching authors:", error);
					this.error = "Failed to load authors.";
				})
				.finally(() => {
					this.isLoading = false;
				});
		},

		async followUser(foreignAuthorId) {
			const authToken = localStorage.getItem("userToken");
			const currentUser = localStorage.getItem("userId");

			try {
				// Construct the follow request object
				const followRequest = {
					type: "Follow",
					summary: `${currentUser} wants to follow you.`,
					actor: currentUser,
					object: foreignAuthorId,
				};
				// Send the follow request to the inbox of the user being followed
				const response = await axios.post(`${this.HOST_URL}/authors/${foreignAuthorId}/inbox/`, followRequest, {
					headers: {
						Authorization: `Token ${authToken}`,
					},
				});
				// Update UI or perform any other necessary actions
				alert("Follow request sent successfully!");
				this.pendingRequests.push(foreignAuthorId);
			} catch (error) {
				console.error("Error sending follow request:", error);
				// Handle error scenarios
				if (error.response) {
					// The request was made and the server responded with a status code
					// that falls out of the range of 2xx
					alert(
						`Error: ${
							error.response.data.detail || "Failed to send follow request. Please try again later."
						}`
					);
				} else if (error.request) {
					// The request was made but no response was received
					console.log(error.request);
					alert("No response from the server. Please check your network connection.");
				} else {
					// Something happened in setting up the request that triggered an Error
					console.log("Error", error.message);
					alert("An error occurred. Please try again later.");
				}
			}
		},
		//Fetches everyone following status 2 & 3
		async fetchPending() {
			try {
				const response = await axios.get(`${this.HOST_URL}/authors/${this.currentUser}/requests/pending`, {
					headers: { Authorization: `Token ${localStorage.getItem("userToken")}` },
				});
				console.log("This is pending", response.data);
				this.pendingRequests = response.data.map((follow) => follow.object.uid);
				console.log("pending requests: ", this.pendingRequests);
				//this.pendingRequests = response.data.map()
			} catch (error) {
				console.error("Error fetching pending list:", error);
			}
		},
		async fetchLikesForPost(post) {
			const authToken = localStorage.getItem("userToken");

			try {
				const response = await axios.get(
					`${this.HOST_URL}/authors/${post.author.uid}/posts/${this.getPostId(post.id)}/likes`,
					{
						headers: {
							Authorization: `Token ${authToken}`,
						},
					}
				);
				post.likesCount = response.data.length;
				post.likes = response.data;
			} catch (error) {
				console.error("Error fetching likes for post:", error);
			}
		},
		async initializeLikecount() {
			for (let post of this.userPosts) {
				console.log("initializelikecount");
				await this.fetchLikesForPost(post);
			}
		},
		async fetchUserLikes() {
			const userId = localStorage.getItem("userId");
			const authToken = localStorage.getItem("userToken");

			console.log(userId, authToken);

			try {
				const response = await axios.get(`${this.HOST_URL}/authors/${userId}/liked`, {
					headers: { Authorization: `Token ${authToken}` },
				});

				const likedItems = response.data.items;
				console.log("liked items" + likedItems);
				this.userPosts.forEach((post) => {
					// Check if the post is liked by the user
					post.userHasLiked = likedItems.some((item) => item.object === post.id);

					// Check if the comments are liked by the user
					post.comments.forEach((comment) => {
						comment.userHasLiked = likedItems.some((item) => item.object === comment.id);
					});
				});
			} catch (error) {
				console.error("Error fetching user likes:", error);
			}
		},

		isCurrentUserAuthor(authorId) {
			const userId = localStorage.getItem("userId");
			return userId === authorId;
		},
		isImageContentType(contentType) {
			return contentType === "image/png;base64" || contentType === "image/jpeg;base64";
		},
		isImageContentType(contentType) {
			return contentType.startsWith("image/");
		},
		async fetchFollowingList() {
			try {
				const authorId = this.$route.params.authorId;
				const authToken = localStorage.getItem("userToken");

				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}

				const response = await axios.get(`${this.HOST_URL}/authors/${this.currentUser}/following/`, {
					headers: { Authorization: `Token ${localStorage.getItem("userToken")}` },
				});
				this.followedAuthors = response.data.map((following) => following.object.uid);
			} catch (error) {
				console.error("Error fetching following list:", error);
			}
		},

		formatDate(value) {
			if (value) {
				// Use 'en-US' locale to get the U.S. date and time format
				return new Date(value).toLocaleString("en-US", {
					month: "numeric", // Numeric month (e.g., 3)
					day: "numeric", // Numeric day (e.g., 18)
					year: "numeric", // 4-digit year (e.g., 2024)
					hour: "2-digit", // 2-digit hour
					minute: "2-digit", // 2-digit minute
					second: "2-digit", // 2-digit second
					hour12: true, // Use 12-hour time format
				});
			}
			return "";
		},

		renderMarkdown(content) {
			return DOMPurify.sanitize(marked(content));
		},
		async likePost(post) {
			// Construct the like object
			const likeObject = {
				summary: `${this.currentUser} Likes your post`,
				type: "Like",
				author: {
					type: "author",
					id: `${this.HOST_URL}/authors/${this.currentUser}`,
					host: this.HOST_URL,
				},
				object: post.id,
			};

			console.log("Like object: ", likeObject);

			try {
				const response = await axios.post(`${this.HOST_URL}/authors/${post.author.uid}/inbox/`, likeObject, {
					headers: {
						Authorization: `Token ${localStorage.getItem("userToken")}`,
						"Content-Type": "application/json",
					},
				});
				console.log("Like successful: ", response.data);
				post.userHasLiked = true;
				post.likesCount += 1;
			} catch (error) {
				console.error("Error sending like for post: ", error);
			}
		},
		async fetchUserPosts() {
			try {
				// Retrieve the authentication token, if required
				const authToken = localStorage.getItem("userToken");
				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}

				// Fetch a single post details, including the Authorization header if needed
				const response = await axios.get(
					`${this.HOST_URL}/authors/${this.$route.params.authorId}/posts/${this.postId}`,
					{
						headers: {
							Authorization: `Token ${localStorage.getItem("userToken")}`,
						},
					}
				);

				// Update the post data with response
				this.post = {
					...response.data,
					comments: [],
					showComments: false,
					commentsLoaded: false,
					commentsError: null,
					newComment: "",
					newCommentContentType: "text/plain",
					pagination: {
						currentPage: 1,
						totalPages: Math.ceil(response.data.count / 5), // Assuming `count` is the number of comments
					},
					userHasLiked: false,
					likesCount: 0,
				};
				console.log("post data " + JSON.stringify(response.data));
				// Call methods to fetch likes and comments for the post
				await this.fetchLikesForPost(this.post);
				await this.fetchUserLikes();
				// Optionally, fetch comments here if they are not loaded on-demand
			} catch (error) {
				console.error("Error fetching post details:", error);
			}
		},
		async fetchFollowers() {
			// Implement fetching followers from the backend API
			try {
				const authorId = localStorage.getItem("userId");
				const authToken = localStorage.getItem("userToken");

				if (!authToken) {
					console.error("Authentication token not found.");
					return;
				}
				const response = await axios.get(`${this.HOST_URL}/authors/${authorId}/followers`, {
					headers: { Authorization: `Token ${authToken}` },
				});
				// console.log('Followers:', response.data)
				this.followers = response.data.items.map((item) => ({
					uid: item.uid,
					username: item.username,
					displayName: item.displayName,
					//profilePhoto: item.profileImage,
				}));
			} catch (error) {
				console.error("Error fetching followers:", error);
			}
		},
		async fetchFriendsList() {
			try {
				const response = await axios.get(`${this.HOST_URL}/authors/${this.currentUser}/friends/`, {
					headers: { Authorization: `Token ${localStorage.getItem("userToken")}` },
				});
				// console.log("RESPONSEYEYY: ,", response.data)
				this.friendsList = response.data
					.filter((item) => item.object.uid !== this.currentUser)
					.map((item) => ({
						uid: item.object.uid,
						username: item.object.username,
						displayName: item.object.displayName,
						profilePhoto: item.object.profileImage,
					})); // Log the list of friends to the console
				console.log("List of Friends:", this.friendsList);
			} catch (error) {
				console.error("Error fetching friends list:", error);
			}
		},
	},
};
</script>

<style scoped>
.create-post-container {
	background-color: #fff;
	border: 1px solid #ccc;
	border-radius: 10px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	padding: 20px;
	margin-bottom: 20px; /* Add margin bottom for spacing between posts */
}

.post-header {
	display: flex;
	align-items: center;
	margin-bottom: 15px;
}

.author-profile-picture {
	width: 40px;
	height: 40px;
	border-radius: 50%;
	object-fit: cover;
	margin-right: 10px;
}
.post-profile-picture {
	border-radius: 50%;
	width: 40px;
	height: 40px;
	object-fit: cover;
	border: 2px solid #ddd;
	margin-right: 10px;
}

h1 {
	font-size: 28px; /* Adjust the font size for the post title */
	margin-top: 0; /* Remove default margin for the title */
	margin-bottom: 20px; /* Add margin bottom for spacing */
	font-weight: bold; /* Make the title bold */
	text-align: left;
}

h3 {
	margin-top: 0; /* Remove default margin for headings */
	font-weight: bold;
}

.post-content h3,
.post-content p {
	margin-top: 0;
}

.post-content p {
	white-space: pre-wrap;
}

.post-title {
	font-size: 23px;
	margin-left: 3px;
	margin-bottom: 10px;
	font-weight: bold;
}

img {
	max-width: 100%;
	max-height: 300px;
	margin-top: 10px;
}

p {
	margin: 0; /* Remove default margin for paragraphs */
	margin-bottom: 10px; /* Add margin bottom for spacing between paragraphs */
}

strong {
	font-weight: bold; /* Make strong text bold */
}

.author-username {
	margin: 0; /* Remove default margin */
	margin-bottom: 0px; /* Add margin bottom for spacing */
	margin-left: 5px;
	margin-top: 17px;
}

.post-info {
	flex-grow: 1;
}

.post-username {
	margin: 0;
	font-weight: bold;
}

.post-timestamp {
	margin: 0;
	font-size: 0.85em;
	color: #606770;
}
.post-image {
	max-width: 100%;
	height: auto;
	margin-top: 10px;
}

.following-button {
	font-size: 0.8em;
	color: #811699;
	/* Set the color to match the border color */
	margin-right: 7px;
	border-radius: 9px;
	padding: 4px 6px;
	background-color: transparent;
	/* Remove background color */
	border: none;
	/* Remove border */
	margin-top: -5px;
	/* Adjust the margin-top to move the button up */
}

.following-button:hover {
	background-color: rgba(0, 123, 255, 0.1);
	/* Optional: Add a background color on hover */
}

.following-button i {
	color: #21a749;
	/* Set the color of the icon to match the border color */
}

.verify-icon {
	color: #007bff;
	margin-left: 5px;
}

.post-actions {
	display: flex;
	gap: 10px;
}
.like-button {
	background-color: #f0f0f0;
	border: 1px solid #ccc;
	cursor: pointer;
	padding: 5px 10px;
	border-radius: 5px;
	display: flex;
	align-items: center;
	margin-top: 10px;
}
.like-button:hover {
	background-color: #e0e0e0;
}

.active {
	background-color: #4caf50;

	color: white;
}

.like-button:disabled {
	cursor: not-allowed;
}

.liked > .fa-heart {
	color: red;
}

.follow-button {
	font-size: 0.8em;
	color: #ffffff;
	margin-right: 7px;
	border-radius: 9px;
	padding: 4px 6px;
	background-color: #28a745;
}

.follow-button:hover {
	background-color: #218838;
	/* Darker green color on hover */
	font-size: 0.8em;
	color: #ffffff;
	margin-right: 7px;
	border-radius: 9px;
	padding: 4px 6px;
	background-color: #28a745;
}

.follow-button:hover {
	background-color: #218838;
}
.pending-button {
	font-size: 0.8em;
	color: #ffffff;
	margin-right: 7px;
	border-radius: 9px;
	padding: 4px 6px;
	background-color: #763180;
	/* Yellow color for pending */
}

.pending-button:hover {
	background-color: #4d0c58;
	/* Darker yellow color on hover */
}

.following-button {
	font-size: 0.8em;
	color: #811699;
	/* Set the color to match the border color */
	margin-right: 7px;
	border-radius: 9px;
	padding: 4px 6px;
	background-color: transparent;
	/* Remove background color */
	border: none;
	/* Remove border */
	margin-top: -5px;
	/* Adjust the margin-top to move the button up */
}

.following-button:hover {
	background-color: rgba(0, 123, 255, 0.1);
	/* Optional: Add a background color on hover */
}

.following-button i {
	color: #21a749;
	/* Set the color of the icon to match the border color */
}
.share-post-button {
	font-size: 0.8em;
	color: #ffffff;
	margin-right: 7px;
	border-radius: 9px;
	padding: 4px 6px;
	background-color: #3492c5;
}

.share-post-button:hover {
	background-color: #3087b5;
}
.comment {
	padding: 10px 0;
	border-bottom: 1px solid #eee;
}

/* Pagination Controls */
.pagination-controls {
	display: flex;
	justify-content: center;
	margin-top: 15px;
}

.pagination-controls button {
	margin: 0 5px;
	padding: 5px 10px;
	background-color: #f0f0f0;
	border: 1px solid #ddd;
	border-radius: 5px;
	cursor: pointer;
}

.pagination-controls button:hover {
	background-color: #e0e0e0;
}

.error-message {
	color: #d9534f;
	margin-bottom: 15px;
}

.view-comments-button {
	background-color: #f0f0f0;
	border: 1px solid #ccc;
	cursor: pointer;
	padding: 5px 10px;
	border-radius: 5px;
	display: flex;
	align-items: center;
	margin-top: 10px;
}

.view-comments-button:hover {
	background-color: #e0e0e0;
}

.view-comments-button i {
	margin-right: 5px;
}

.comments-section {
	margin-top: 20px;
	background-color: #f9f9f9;
	padding: 10px;
	border-radius: 5px;
}

.comment {
	padding-bottom: 10px;
	margin-bottom: 10px;
	border-bottom: 1px solid #eee;
}

.view-comments-button.active {
	background-color: #54bbff;
}
.comment-form-title {
	font-size: 18px;
	margin-bottom: 10px;
}

.input-group {
	margin-bottom: 15px;
}

.input-style {
	width: 100%;
	padding: 8px 12px;
	border: 1px solid #ccc;
	border-radius: 4px;
	margin-bottom: 10px;
	box-sizing: border-box;
}

.submit-comment-button {
	background-color: #4caf50;
	border: none;
	color: white;
	padding: 10px 20px;
	text-align: center;
	text-decoration: none;
	display: inline-block;
	font-size: 16px;
	margin: 4px 2px;
	cursor: pointer;
	border-radius: 4px;
}

.comments-section {
	background-color: #eeeded;
	border: 1px solid #ccc;
	border-radius: 10px;
	padding: 15px;
	margin-top: 20px;
}

.comment {
	border-bottom: 1px solid #999999;
	padding-bottom: 10px;
	margin-bottom: 10px;
}

.comment:last-child {
	border-bottom: none;
}

.comment strong {
	font-weight: bold;
}

.comment p {
	margin: 0;
}

.pagination-controls {
	display: flex;
	justify-content: center;
	margin-top: 20px;
}

.pagination-button {
	background-color: #f0f0f0;
	border: 1px solid #ddd;
	border-radius: 5px;
	cursor: pointer;
	padding: 5px 10px;
	margin: 0 5px;
}

.pagination-button:hover {
	background-color: #e0e0e0;
}
</style>
