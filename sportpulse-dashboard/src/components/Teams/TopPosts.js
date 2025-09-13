import React from "react";

const TopPosts = () => {
  const posts = [
    {
      name: "Ava Harper",
      time: "2h ago",
      text: "The energy at the stadium is electric! #GameDayFever",
      likes: 120,
      dislikes: 5,
      img: "https://lh3.googleusercontent.com/aida-public/AB6AXuDWqtl6iBx7XHZ_k0Vxd4O-_YigleGg9h4uvaDJEy1dm9X9sRAO3x6PgUlzc_IpK2V6QiA2X12LhcDlQOTdQjBVr422pxWCj-57fWzQRRt-ZJZRdv7EDeRMPwbc8ARgO5gVBdeHYGE15s6e8Q-d8mnH5BwtJWV-xjxRJliDwecBM5hvuZsoQ8z3HbvgZnQghM5TvKRgXWEdE0FDGb0y2ZfDnOIQUE9g818CG_t5EWX-jDghGrO8-ICJgmbGwooRQ4JC_C6h1WuPlaeT",
    },
    {
      name: "Owen Turner",
      time: "3h ago",
      text: "Massive win for the team! #GameDayFever #VictoryLap",
      likes: 250,
      dislikes: 10,
    },
    {
      name: "Chloe Foster",
      time: "4h ago",
      text: "So proud of our players! #GameDayFever #TeamSpirit",
      likes: 180,
      dislikes: 2,
    },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Top Posts</h2>
      <div className="space-y-4">
        {posts.map((post, index) => (
          <div
            key={index}
            className="flex items-start gap-4 p-4 bg-[#1e293b] rounded-lg"
          >
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <p className="font-bold text-sm">{post.name}</p>
                <p className="text-gray-500 text-xs">{post.time}</p>
              </div>
              <p className="text-gray-300 text-sm mb-3">{post.text}</p>
              <div className="flex gap-6">
                <div className="flex items-center gap-2 text-gray-400">
                  <span className="material-symbols-outlined text-base">
                    likes
                  </span>
                  <span className="text-xs">{post.likes}</span>
                </div>
                <div className="flex items-center gap-2 text-gray-400">
                  <span className="material-symbols-outlined text-base">
                    dislike
                  </span>
                  <span className="text-xs">{post.dislikes}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopPosts;
