%
%  Surfaces Convex Hull calculation for Imaris 7 by Niko Ehrenfeuchter
%
%  Requirements:
%    - IceImarisConnector (https://github.com/aarpon/IceImarisConnector)
%

function IceXTSurfacesConvexHull()
	ver = 1; % internal version number
	
	% start Imaris and set up the connection
	conn = IceImarisConnector();
	conn.startImaris();

	% wait until the connection is ready and the user has selected some data
    msg = 'Click "OK" to continue after opening a dataset and ' ...
        'selecting a Surface object.'
	ans = questdlg(msg, 'Waiting for Imaris...', 'OK', 'Cancel', 'OK')
	switch ans
		case 'OK'
			extractSurfaces(conn.mImarisApplication);
	end
end

function extractSurfaces(vImApp)
	vFactory = vImApp.GetFactory;
	vSurfaces = vFactory.ToSurfaces(vImApp.GetSurpassSelection);
	vSurpassScene = vImApp.GetSurpassScene;

	% check if a surface was selected in imaris:
    if ~vFactory.IsSurfaces(vSurfaces)
		% otherwise try all elements and take the first surface object:
        for vChildIndex = 1:vSurpassScene.GetNumberOfChildren
			vDataItem = vSurpassScene.GetChild(vChildIndex - 1);
			if vFactory.IsSurfaces(vDataItem)
				vSurfaces = vFactory.ToSurfaces(vDataItem);
				break;
			end
		end
		
		% check if there was a surface at all
		if isequal(vSurfaces, [])
			msgbox('Could not find any Surface!');
			return;
		end
    end
    
    % NOTE: GetNumberOfSurfaces returns the number of surfaces in this
    % surface object, NOT the number of surface objects in the scene
		
    % extract positions of surface points for each and store them
	for SurfaceID = 0:(vSurfaces.GetNumberOfSurfaces - 1)
		vSurfaceVertices = vSurfaces.GetVertices(SurfaceID);
        vSurfaceTriangles = vSurfaces.GetTriangles(SurfaceID);
		fname = sprintf('surface-%d-vertices.csv', SurfaceID);
		csvwrite(fname, vSurfaceVertices)
        fname = sprintf('surface-%d-triangles.csv', SurfaceID);
        csvwrite(fname, vSurfaceTriangles)
	end

end

% vSurfaces = vFactory.ToSurfaces(conn.mImarisApplication.GetSurpassSelection)
% vSurfaces.GetNumberOfSurfaces

% vSurfaceVertices = vSurfaces.GetVertices(0);
% vConvexHull = convhulln(double(vSurfaceVertices));
% vNumberOfPoints = size(vSurfaceVertices, 1)
% vPoints = false(vNumberOfPoints, 1);
% vPoints(vConvexHull(:)) = true
% vPoints = find(vPoints)
% vVertices = vSurfaceVertices(vPoints, :);
% vPointsMap = zeros(vNumberOfPoints, 1);
% vPointsMap(vPoints) = 1:numel(vPoints);
% vTriangles = vPointsMap(vConvexHull(:, [1, 3, 2])) - 1;
% vPointsMap = zeros(vNumberOfPoints, 1);
% vPointsMap(vPoints) = 1:numel(vPoints)
% vMean = mean(vVertices, 1)
% vNormals = [vVertices(:, 1) - vMean(1), vVertices(:, 2) - vMean(2), ...
%     vVertices(:, 3) - vMean(3)];
% vIndexT = vSurfaces.GetTimeIndex(0)
% vSurfaceHull = vFactory.CreateSurfaces
% vSurfaceHull.AddSurface(vVertices, vTriangles, vNormals, vIndexT)
% vSurfaceHull.SetName(['Convex Hull of "Surfaces 4"'])
% vSurfaceHull.SetColorRGBA(vSurfaces.GetColorRGBA);
% vSurfaceHull.SetColorRGBA(vSurfaces.GetColorRGBA)
% vSurfaces.GetParent.AddChild(vSurfaceHull, -1)