# Neighborhood Lost Pets Feature Requirements

## User Posts

- **Create/Edit a post of their lost pet:**
    These posts should contain this information about the pet: animal (cat/dog), name of pet, breed, appearance info (color, eyes, etc, last seen location (displayed as distance from current viewer), date (how long ago), contact info, and other relevant information. Posts should also have photos, and a map that displays the approximate location (do not show exact location for privacy). There should be some form of status indicator showing whether the pet is lost or has be reunited with their owner. All of this information should be editable (including delete) by the user that created the post. Contact info can be hidden for privacy if desired.

- **Save post for later viewing:**
    Users should be able to save a post they're viewing so that they can easily keep track of it and view it later.

- **Comments:**
    Users should be able to leave comments and view them on a post. Users should also be able to reply to other comments (displayed in a nested fashion).

- **Reactions:**
    Users should be able to react to posts with their preferred emotion (like, heart, sad, angry).

- **Contact owner:**
    Users should be able to contact the owner of a lost pet using contact information displayed on the post or by using the built-in private messaging system (see details below).


## Main Feed

- **Display posts of nearby pets:**
    Only posts that are within the user-specified search radius should be shown.

- **Order posts by date & time:**
    Posts should be listed in date-descending order (newer posts displayed first).

- **Feed filter settings:**
    Users should be able to adjust the parameters for which posts are shown. This includes: distance from user, date & time created, type of pet (cat/dog).


## Custom Search

- **Search posts using specified parameters:**
    Users should be able to search for all posts containing specific information, such as animal type, breed, date, etc.). This function should also accept ranges of values (e.g. search all posts from 01/01/21 to 01/30/21). This search function should allow the user to accurately find the information they are looking for.


## Private Messaging

- **Contact post author via message:**
    Users should be able to contact a post author using private messages. This is an alternative to using any publicly displayed contact information on the post.

- **One-to-one messaging:** 
    Private messaging only needs to support one-to-one conversations.


## Notifications

- **Users should receive a notification from any of the following:**
  - a private message was received
  - a user comments on their post
  - a saved post's status is changed

- **All notifications should be optional:**
    Users should be able to disable any and all notifications if desired.