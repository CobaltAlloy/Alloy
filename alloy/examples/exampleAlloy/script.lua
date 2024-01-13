BLASTER_MG = {
	initMethod = function(self)
		METH.initGenericWeapon(self)
	end,
	updateMethod = function(self, actor, time)
		self:updateRecoil(actor, time)
	end,
	useMethod = function(self, actor, angle)
		actor:emitSound(self:getUseSound(), 1, 1, self:getSoundRange())

		local rec = self:getRecoilAmount()

		actor:setStealthPenalty(self:getSoundRange() * SoundToVisFactor + rec * RecoilToVisFactor)

		local x, y = actor:getSafeWeaponXY()
		local obj = actor:shootProjectedBullet(x, y, angle, self.bulletSpeed, self.bullet, self)

		self:createMuzzleFx(actor, x, y, "blasterMuzzle", 1, angle)
		self:applyRandomRecoil(actor, rec)
		self:applyRecoilFatigue()
		self:useAmmo(actor, 1)

		return true
	end,
	customSpriteNames = {
		back = "plasmaAccelerator_back",
		light = "plasmaAccelerator_light",
		mag = "blastgun_magazine2"
	},
	renderMethod = function(self, x, y, angle, r, g, b, facingRight, glow)
		local cusprites = self.def.customSprites

		video.renderSpriteState(cusprites.back, x, y, 1, angle, 255, r, g, b, not facingRight)
		video.renderSpriteState(self.def.sprite, x, y, 1, angle, 255, r, g, b, not facingRight)
		video.renderSpriteState(cusprites.light, x, y, 1, angle, 255, r, g, b, not facingRight)
		video.renderSpriteState(cusprites.mag, x, y, 1, angle, 255, r, g, b, not facingRight)
	end
}

local greet = AlloyRegisterOption("exampleAlloy", { type = "toggle", value = true, name = "Greet user" }).value
if greet then print("ALLOY -- Hello from the test and example alloy! :D") end

-- this is the culmination of looking at how to render respawn counters like modeStates.lua line 1526
local forceHud = AlloyRegisterOption("exampleAlloy", { type = "toggle", value = false, name = "Force hud" }).value
if forceHud then
	_config.showHud = true
end

hook.add("frameUpdate", function(time)
	if forceHud then
		local game = states.get("game")
		if game and game.cameraMode and not game.cameraMode.settings.hudBots then
			game.cameraMode.settings.hudBots = true
		end
	end
end)
