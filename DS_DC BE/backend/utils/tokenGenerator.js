import jwt from "jsonwebtoken";

export const generateTokenAndSetCookie = (user_id, roles, res) => {
  const isDev = process.env.NODE_ENV === "development";

  const token = jwt.sign(
    { userId: user_id, roles },
    process.env.JWT_SECRET,
    { expiresIn: "15d" }
  );

  res.cookie("jwt", token, {
    httpOnly: true,
    secure: !isDev,         // true in production, false in development
    sameSite: "strict",     // more secure than 'lax'
    maxAge: 15 * 24 * 60 * 60 * 1000, // 15 days
    path: "/"               // make cookie available across all paths
  });

  // Log token details for debugging
  const decoded = jwt.decode(token);
  console.log("Token generated for user:", {
    userId: decoded.userId,
    roles: decoded.roles,
    expiresIn: decoded.exp
  });
};
