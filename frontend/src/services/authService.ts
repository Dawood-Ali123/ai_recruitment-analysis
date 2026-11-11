import api from "./api";

interface LoginData {
  email: string;
  password: string;
}

export const loginUser = async (data: LoginData) => {
  const response = await api.post("/auth/login", data);

  // Save JWT token
  localStorage.setItem("access_token", response.data.access_token);

  // Get logged-in user information
  const userResponse = await api.get("/auth/me", {
    headers: {
      Authorization: `Bearer ${response.data.access_token}`,
    },
  });

  localStorage.setItem("user", JSON.stringify(userResponse.data));

  return userResponse.data;
};