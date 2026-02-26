import { apiClient } from './apiClient';

const ENDPOINTS = {
  ARTICLES: '/blog/articles/',
  CATEGORIES: '/blog/categories/',
  TUTORIALS: '/blog/tutorials/',
};

export const blogService = {
  getArticles: async (params = {}) => {
    // پارامترهایی مثل search, page, ordering, category اینجا به بک‌اند ارسال میشن
    const response = await apiClient.get(ENDPOINTS.ARTICLES, { params });
    return response.data;
  },

  getArticleById: async (id) => {
    const response = await apiClient.get(`${ENDPOINTS.ARTICLES}${id}/`);
    return response.data;
  },

  getCategories: async () => {
    const response = await apiClient.get(ENDPOINTS.CATEGORIES);
    return response.data;
  },

  getCategoryById: async (id) => {
    const response = await apiClient.get(`${ENDPOINTS.CATEGORIES}${id}/`);
    return response.data;
  },

  getTutorials: async (params = {}) => {
    const response = await apiClient.get(ENDPOINTS.TUTORIALS, { params });
    return response.data;
  },

  getTutorialById: async (id) => {
    const response = await apiClient.get(`${ENDPOINTS.TUTORIALS}${id}/`);
    return response.data;
  }
};