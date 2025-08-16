import { useAuth as useClerkAuth, useUser } from '@clerk/clerk-react';
import { useState, useEffect } from 'react';

export const useAuth = () => {
  const { isSignedIn, userId, getToken, signOut } = useClerkAuth();
  const { user, isLoaded } = useUser();
  const [authToken, setAuthToken] = useState(null);

  useEffect(() => {
    const fetchToken = async () => {
      if (isSignedIn && userId) {
        try {
          const token = await getToken();
          setAuthToken(token);
        } catch (error) {
          console.error('Error fetching auth token:', error);
        }
      } else {
        setAuthToken(null);
      }
    };

    fetchToken();
  }, [isSignedIn, userId, getToken]);

  const logout = async () => {
    try {
      await signOut();
      setAuthToken(null);
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  return {
    isAuthenticated: isSignedIn,
    user,
    userId,
    authToken,
    isLoaded,
    logout,
    getToken
  };
};

export const useAuthenticatedUser = () => {
  const { user, isAuthenticated, isLoaded } = useAuth();
  
  const [userProfile, setUserProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);

  useEffect(() => {
    if (isLoaded && isAuthenticated && user) {
      // Extract user information from Clerk
      const profile = {
        id: user.id,
        email: user.primaryEmailAddress?.emailAddress,
        firstName: user.firstName,
        lastName: user.lastName,
        fullName: user.fullName,
        imageUrl: user.imageUrl,
        createdAt: user.createdAt,
        lastSignInAt: user.lastSignInAt
      };
      
      setUserProfile(profile);
      setProfileLoading(false);
    } else if (isLoaded && !isAuthenticated) {
      setUserProfile(null);
      setProfileLoading(false);
    }
  }, [user, isAuthenticated, isLoaded]);

  return {
    userProfile,
    profileLoading,
    isAuthenticated,
    isLoaded
  };
};