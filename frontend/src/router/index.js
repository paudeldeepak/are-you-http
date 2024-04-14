import { createRouter, createWebHistory } from "vue-router";
import SignUpView from "../views/SignUpView.vue";
import SignInView from "../views/SignInView.vue";
import HomePage from "../views/HomePage.vue";
import ProfileView from "../views/ProfileView.vue";
import PostsView from "../views/PostsView.vue";
import StreamView from "../views/StreamView.vue";
import CreatePostsView from "../views/CreatePostsView.vue";
import EditProfileView from "../views/EditProfileView.vue";
import EditPostView from "../views/EditPostView.vue";
import InboxView from "../views/InboxView.vue";
import ConnectionsView from "../views/ConnectionsView.vue";




const router = createRouter({
	history: createWebHistory('/'),
	routes: [
		{
			path: "/signup",
			name: "signup",
			component: SignUpView,
		},
		{
			path: "/signin",
			name: "signin",
			component: SignInView,
		},

		{
			path: "/profile/:authorId",
			name: "profile",
			component: ProfileView,
			props: true,
		},

		{
			path: "/",
			name: "home",
			component: HomePage,
		},

		{
			path: "/stream",
			name: "stream",
			component: StreamView,
		},

		{
			path: "/posts/:authorId/:postId",
			name: "posts",
			component: PostsView,
			props: true,
		},

		{
			path: "/create-post",
			name: "create-post",
			component: CreatePostsView,
		},

		{
			path: "/edit-profile/:authorId",
			name: "edit-profile",
			component: EditProfileView,
			props: true,
		},

		{
			path: "/inbox/:authorId",
			name: "inbox",
			component: InboxView,
			props: true,
		},

		{
			path: "/authors/:authorId/posts/:postId/edit",
			name: "edit-post",
			component: EditPostView,
			props: true,
		},

		{
			path: "/connections",
			name: "connections",
			component: ConnectionsView,

		},

	],
});

export default router;